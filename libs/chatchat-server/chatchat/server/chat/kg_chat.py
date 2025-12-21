"""
知识图谱对话模块
将知识图谱作为外部知识源，辅助LLM进行问答
"""
from __future__ import annotations

import asyncio
import json
from typing import AsyncIterable, List, Optional
from urllib.parse import urlencode

from fastapi import Body, Request
from fastapi.concurrency import run_in_threadpool
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.prompts.chat import ChatPromptTemplate
from sse_starlette.sse import EventSourceResponse

from chatchat.server.api_server.api_schemas import OpenAIChatOutput
from chatchat.server.chat.utils import History
from chatchat.server.knowledge_base.kg_service import KnowledgeGraphService
from chatchat.server.utils import (
    BaseResponse,
    get_ChatOpenAI,
    get_default_llm,
    get_prompt_template,
    wrap_done,
)
from chatchat.settings import Settings


def get_kg_chat_prompt() -> str:
    """获取知识图谱对话的提示词模板"""
    return """你是一个智能助手，可以利用知识图谱中的结构化知识来回答用户问题。

知识图谱上下文:
{context}

历史对话:
{history}

用户问题: {question}

请基于知识图谱中的信息，准确、详细地回答用户问题。如果知识图谱中没有相关信息，请如实告知。
在回答时，请充分利用图谱中的实体关系，提供有逻辑性和连贯性的答案。

回答:"""


async def kg_chat(
    query: str = Body(..., description="用户输入", examples=["张三认识哪些人？"]),
    kb_name: str = Body(..., description="知识库名称", examples=["samples"]),
    top_k: int = Body(10, description="返回相关节点数量"),
    history: List[History] = Body(
        [],
        description="历史对话",
        examples=[
            [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
            ]
        ],
    ),
    stream: bool = Body(True, description="流式输出"),
    model: str = Body(get_default_llm(), description="LLM 模型名称"),
    temperature: float = Body(
        Settings.model_settings.TEMPERATURE, description="LLM 采样温度", ge=0.0, le=2.0
    ),
    max_tokens: Optional[int] = Body(
        Settings.model_settings.MAX_TOKENS,
        description="限制LLM生成Token数量，默认None代表模型最大值",
    ),
    prompt_name: str = Body(
        "default", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"
    ),
    request: Request = None,
):
    """
    知识图谱对话接口
    
    利用知识图谱中的结构化知识辅助LLM回答问题
    """

    async def kg_chat_iterator() -> AsyncIterable[str]:
        nonlocal max_tokens
        callback = AsyncIteratorCallbackHandler()

        # 获取知识图谱服务
        kg_service = KnowledgeGraphService(kb_name=kb_name)

        # 从知识图谱中获取相关上下文
        context = await run_in_threadpool(
            kg_service.get_graph_context_for_llm, query=query, top_k=top_k
        )

        # 构建历史对话文本
        history_text = "\n".join(
            [f"{h['role']}: {h['content']}" for h in history]
        )

        # 构建提示词
        prompt_template = get_kg_chat_prompt()
        prompt = ChatPromptTemplate.from_template(prompt_template)

        # 获取LLM
        llm = get_ChatOpenAI(
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
        )

        # 构建最终的输入
        messages = prompt.format_messages(
            context=context if context else "暂无相关知识图谱信息",
            history=history_text if history_text else "无历史对话",
            question=query,
        )

        # 创建任务
        task = asyncio.create_task(
            wrap_done(llm.agenerate(messages=[messages]), callback.done)
        )

        source_documents = []

        # 流式输出
        if stream:
            async for token in callback.aiter():
                # 根据客户端是否断开连接，避免报错
                if await request.is_disconnected():
                    break
                yield json.dumps(
                    OpenAIChatOutput(
                        id=f"chat{id}",
                        model=model,
                        choices=[
                            {
                                "index": 0,
                                "delta": {"role": "assistant", "content": token},
                            }
                        ],
                    ).model_dump(),
                    ensure_ascii=False,
                )
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps(
                OpenAIChatOutput(
                    id=f"chat{id}",
                    model=model,
                    choices=[
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": answer},
                            "finish_reason": "stop",
                        }
                    ],
                ).model_dump(),
                ensure_ascii=False,
            )

        await task

        # 如果需要记录来源
        if context:
            yield json.dumps(
                {
                    "type": "source",
                    "data": {
                        "kb_name": kb_name,
                        "query": query,
                        "context_preview": context[:500] + "..."
                        if len(context) > 500
                        else context,
                    },
                },
                ensure_ascii=False,
            )

    return EventSourceResponse(kg_chat_iterator())


async def simple_kg_query(
    query: str = Body(..., description="用户输入", examples=["张三"]),
    kb_name: str = Body(..., description="知识库名称", examples=["samples"]),
    top_k: int = Body(10, description="返回相关节点数量"),
):
    """
    简单的知识图谱查询接口（不使用LLM）
    
    直接返回知识图谱中的相关信息
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        
        # 搜索相关节点
        nodes = kg_service.search_nodes(keyword=query, limit=top_k)
        
        # 获取相关的边
        edges = []
        for node in nodes:
            node_edges = kg_service.list_edges(node_id=node["node_id"], limit=20)
            edges.extend(node_edges)
        
        # 去重边
        unique_edges = []
        seen = set()
        for edge in edges:
            edge_key = (edge["source_node_id"], edge["target_node_id"], edge["relation_type"])
            if edge_key not in seen:
                seen.add(edge_key)
                unique_edges.append(edge)
        
        return BaseResponse(
            code=200,
            msg="查询成功",
            data={
                "nodes": nodes,
                "edges": unique_edges,
                "query": query,
            },
        )
    except Exception as e:
        return BaseResponse(code=500, msg=f"查询失败: {str(e)}")
