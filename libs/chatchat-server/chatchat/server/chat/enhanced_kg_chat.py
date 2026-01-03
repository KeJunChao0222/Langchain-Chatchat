"""
增强型知识对话模块
结合知识图谱和知识库，为LLM提供更丰富的上下文信息
"""
from __future__ import annotations

import asyncio
import json
import uuid
from typing import AsyncIterable, List, Optional, Literal

from fastapi import Body, Request
from fastapi.concurrency import run_in_threadpool
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.prompts.chat import ChatPromptTemplate
from sse_starlette.sse import EventSourceResponse

from chatchat.server.api_server.api_schemas import OpenAIChatOutput
from chatchat.server.chat.utils import History
from chatchat.server.knowledge_base.kb_service.base import KBServiceFactory
from chatchat.server.knowledge_base.kb_doc_api import search_docs
from chatchat.server.knowledge_base.kg_service import KnowledgeGraphService
from chatchat.server.knowledge_base.utils import format_reference
from chatchat.server.utils import (
    BaseResponse,
    get_ChatOpenAI,
    get_default_llm,
    get_prompt_template,
    wrap_done,
    build_logger,
    check_embed_model,
    api_address,
)
from chatchat.settings import Settings


logger = build_logger()


def get_enhanced_chat_prompt() -> str:
    """获取增强型对话的提示词模板"""
    return """你是一个智能助手，可以利用知识图谱中的结构化知识和知识库中的文档内容来回答用户问题。

## 知识图谱上下文（结构化实体和关系）
{kg_context}

## 知识库文档上下文（相关文档片段）
{kb_context}

## 历史对话
{history}

## 用户问题
{question}

## 回答要求
1. 综合利用知识图谱中的实体关系和知识库中的文档内容来回答问题
2. 知识图谱提供了实体之间的结构化关系，可用于理解概念间的联系
3. 知识库文档提供了详细的文本描述，可用于获取具体信息
4. 如果两个来源的信息有冲突，请指出并给出合理的解释
5. 如果没有找到相关信息，请如实告知

回答:"""


async def enhanced_kg_chat(
    query: str = Body(..., description="用户输入", examples=["请介绍一下相关内容"]),
    kb_name: str = Body(..., description="知识库名称", examples=["samples"]),
    use_kg: bool = Body(True, description="是否使用知识图谱"),
    use_kb: bool = Body(True, description="是否使用知识库"),
    kg_top_k: int = Body(10, description="知识图谱返回相关节点数量"),
    kb_top_k: int = Body(Settings.kb_settings.VECTOR_SEARCH_TOP_K, description="知识库匹配向量数"),
    score_threshold: float = Body(
        Settings.kb_settings.SCORE_THRESHOLD,
        description="知识库匹配相关度阈值",
        ge=0.0,
        le=2.0,
    ),
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
    return_direct: bool = Body(False, description="直接返回检索结果，不送入 LLM"),
    request: Request = None,
):
    """
    增强型知识对话接口
    
    同时利用知识图谱和知识库中的信息辅助LLM回答问题
    - 知识图谱：提供结构化的实体和关系信息
    - 知识库：提供相关的文档片段
    """
    
    # 验证知识库是否存在
    if use_kb:
        kb = KBServiceFactory.get_service_by_name(kb_name)
        if kb is None:
            return BaseResponse(code=404, msg=f"未找到知识库 {kb_name}")

    async def enhanced_chat_iterator() -> AsyncIterable[str]:
        nonlocal max_tokens
        
        try:
            # 处理历史对话
            history_list = [History.from_data(h) for h in history]
            
            # 1. 获取知识图谱上下文
            kg_context = ""
            kg_source = None
            if use_kg:
                try:
                    kg_service = KnowledgeGraphService(kb_name=kb_name)
                    kg_context = await run_in_threadpool(
                        kg_service.get_graph_context_for_llm, query=query, top_k=kg_top_k
                    )
                    if kg_context:
                        # 获取相关节点信息作为来源
                        nodes = await run_in_threadpool(
                            kg_service.search_nodes, keyword=query, limit=kg_top_k
                        )
                        kg_source = {
                            "type": "knowledge_graph",
                            "kb_name": kb_name,
                            "node_count": len(nodes),
                            "nodes": [{"id": n["node_id"], "name": n["node_name"], "type": n.get("node_type")} for n in nodes[:5]]
                        }
                except Exception as e:
                    logger.warning(f"获取知识图谱上下文失败: {e}")
                    kg_context = ""
            
            # 2. 获取知识库文档上下文
            kb_context = ""
            source_documents = []
            if use_kb:
                try:
                    kb = KBServiceFactory.get_service_by_name(kb_name)
                    if kb:
                        ok, msg = kb.check_embed_model()
                        if ok:
                            docs = await run_in_threadpool(
                                search_docs,
                                query=query,
                                knowledge_base_name=kb_name,
                                top_k=kb_top_k,
                                score_threshold=score_threshold,
                                file_name="",
                                metadata={},
                            )
                            if docs:
                                kb_context = "\n\n".join([doc["page_content"] for doc in docs])
                                source_documents = format_reference(kb_name, docs, api_address(is_public=True))
                        else:
                            logger.warning(f"嵌入模型检查失败: {msg}")
                except Exception as e:
                    logger.warning(f"获取知识库文档上下文失败: {e}")
                    kb_context = ""
            
            # 如果只需要返回检索结果
            if return_direct:
                result_data = {
                    "kg_context": kg_context if kg_context else "未找到相关知识图谱信息",
                    "kb_docs": source_documents,
                    "kg_source": kg_source,
                }
                yield OpenAIChatOutput(
                    id=f"chat{uuid.uuid4()}",
                    model=None,
                    object="chat.completion",
                    content=json.dumps(result_data, ensure_ascii=False),
                    role="assistant",
                    finish_reason="stop",
                    docs=source_documents,
                ).model_dump_json()
                return
            
            # 3. 构建提示词
            callback = AsyncIteratorCallbackHandler()
            callbacks = [callback]
            
            if max_tokens in [None, 0]:
                max_tokens = Settings.model_settings.MAX_TOKENS
            
            llm = get_ChatOpenAI(
                model_name=model,
                temperature=temperature,
                max_tokens=max_tokens,
                callbacks=callbacks,
            )
            
            # 构建历史对话文本
            history_text = "\n".join(
                [f"{h.role}: {h.content}" for h in history_list]
            ) if history_list else "无历史对话"
            
            # 使用增强型提示词模板
            prompt_template = get_enhanced_chat_prompt()
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            # 格式化上下文
            kg_context_formatted = kg_context if kg_context else "暂无相关知识图谱信息"
            kb_context_formatted = kb_context if kb_context else "暂无相关知识库文档"
            
            # 构建消息
            messages = prompt.format_messages(
                kg_context=kg_context_formatted,
                kb_context=kb_context_formatted,
                history=history_text,
                question=query,
            )
            
            # 创建异步任务
            task = asyncio.create_task(
                wrap_done(llm.agenerate(messages=[messages]), callback.done)
            )
            
            # 准备来源信息
            all_sources = []
            if source_documents:
                all_sources.extend(source_documents)
            if kg_source:
                all_sources.append(f"**知识图谱来源**: 找到 {kg_source['node_count']} 个相关节点")
            
            if not all_sources:
                all_sources.append("<span style='color:red'>未找到相关文档和图谱信息，该回答为大模型自身能力解答！</span>")
            
            # 流式输出
            if stream:
                # 先输出来源信息
                ret = OpenAIChatOutput(
                    id=f"chat{uuid.uuid4()}",
                    object="chat.completion.chunk",
                    content="",
                    role="assistant",
                    model=model,
                    docs=all_sources,
                )
                yield ret.model_dump_json()
                
                # 流式输出回答
                async for token in callback.aiter():
                    if await request.is_disconnected():
                        break
                    ret = OpenAIChatOutput(
                        id=f"chat{uuid.uuid4()}",
                        object="chat.completion.chunk",
                        content=token,
                        role="assistant",
                        model=model,
                    )
                    yield ret.model_dump_json()
            else:
                # 非流式输出
                answer = ""
                async for token in callback.aiter():
                    answer += token
                ret = OpenAIChatOutput(
                    id=f"chat{uuid.uuid4()}",
                    object="chat.completion",
                    content=answer,
                    role="assistant",
                    model=model,
                    docs=all_sources,
                )
                yield ret.model_dump_json()
            
            await task
            
        except asyncio.exceptions.CancelledError:
            logger.warning("streaming progress has been interrupted by user.")
            return
        except Exception as e:
            logger.error(f"error in enhanced kg chat: {e}")
            yield json.dumps({"error": str(e)})
            return

    if stream:
        return EventSourceResponse(enhanced_chat_iterator())
    else:
        return await enhanced_chat_iterator().__anext__()


async def get_combined_context(
    query: str = Body(..., description="查询内容"),
    kb_name: str = Body(..., description="知识库名称"),
    use_kg: bool = Body(True, description="是否使用知识图谱"),
    use_kb: bool = Body(True, description="是否使用知识库"),
    kg_top_k: int = Body(10, description="知识图谱返回相关节点数量"),
    kb_top_k: int = Body(5, description="知识库匹配向量数"),
    score_threshold: float = Body(0.5, description="知识库匹配相关度阈值"),
):
    """
    获取组合上下文接口
    
    返回知识图谱和知识库的组合上下文，供外部使用
    """
    try:
        result = {
            "query": query,
            "kb_name": kb_name,
            "kg_context": None,
            "kb_context": None,
            "kg_nodes": [],
            "kb_docs": [],
        }
        
        # 获取知识图谱上下文
        if use_kg:
            try:
                kg_service = KnowledgeGraphService(kb_name=kb_name)
                kg_context = kg_service.get_graph_context_for_llm(query=query, top_k=kg_top_k)
                nodes = kg_service.search_nodes(keyword=query, limit=kg_top_k)
                result["kg_context"] = kg_context
                result["kg_nodes"] = nodes
            except Exception as e:
                logger.warning(f"获取知识图谱上下文失败: {e}")
        
        # 获取知识库文档上下文
        if use_kb:
            try:
                kb = KBServiceFactory.get_service_by_name(kb_name)
                if kb:
                    ok, msg = kb.check_embed_model()
                    if ok:
                        docs = search_docs(
                            query=query,
                            knowledge_base_name=kb_name,
                            top_k=kb_top_k,
                            score_threshold=score_threshold,
                            file_name="",
                            metadata={},
                        )
                        result["kb_context"] = "\n\n".join([doc["page_content"] for doc in docs])
                        result["kb_docs"] = docs
            except Exception as e:
                logger.warning(f"获取知识库文档上下文失败: {e}")
        
        return BaseResponse(code=200, msg="获取上下文成功", data=result)
    
    except Exception as e:
        logger.error(f"获取组合上下文失败: {e}")
        return BaseResponse(code=500, msg=f"获取上下文失败: {str(e)}")
