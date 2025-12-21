"""
知识图谱API路由
提供知识图谱的增删改查、导入导出、可视化等接口
"""
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Query, Request

from chatchat.server.chat.kg_chat import kg_chat, simple_kg_query
from chatchat.server.knowledge_base.kg_service import KnowledgeGraphService
from chatchat.server.utils import BaseResponse, ListResponse

kg_router = APIRouter(prefix="/knowledge_graph", tags=["Knowledge Graph Management"])


@kg_router.post("/create_node", response_model=BaseResponse, summary="创建图谱节点")
def create_node(
    kb_name: str = Body(..., description="知识库名称", examples=["samples"]),
    node_id: str = Body(..., description="节点唯一标识", examples=["node_1"]),
    node_name: str = Body(..., description="节点名称", examples=["张三"]),
    node_type: Optional[str] = Body(None, description="节点类型", examples=["Person"]),
    properties: Optional[Dict] = Body(None, description="节点属性", examples=[{"age": 30}]),
):
    """
    创建知识图谱节点
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success = kg_service.add_node(
            node_id=node_id,
            node_name=node_name,
            node_type=node_type,
            properties=properties,
        )

        if success:
            return BaseResponse(code=200, msg=f"成功创建节点 {node_name}")
        else:
            return BaseResponse(code=500, msg="创建节点失败")

    except Exception as e:
        return BaseResponse(code=500, msg=f"创建节点时出错: {str(e)}")


@kg_router.post("/create_edge", response_model=BaseResponse, summary="创建图谱边")
def create_edge(
    kb_name: str = Body(..., description="知识库名称", examples=["samples"]),
    source_node_id: str = Body(..., description="源节点ID", examples=["node_1"]),
    target_node_id: str = Body(..., description="目标节点ID", examples=["node_2"]),
    relation_type: Optional[str] = Body(
        None, description="关系类型", examples=["knows"]
    ),
    properties: Optional[Dict] = Body(
        None, description="边属性", examples=[{"since": "2020"}]
    ),
    weight: float = Body(1.0, description="边权重", examples=[1.0]),
):
    """
    创建知识图谱边（关系）
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success = kg_service.add_edge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relation_type=relation_type,
            properties=properties,
            weight=weight,
        )

        if success:
            return BaseResponse(code=200, msg=f"成功创建关系 {relation_type}")
        else:
            return BaseResponse(code=500, msg="创建关系失败")

    except Exception as e:
        return BaseResponse(code=500, msg=f"创建关系时出错: {str(e)}")


@kg_router.get("/get_node", response_model=BaseResponse, summary="获取节点信息")
def get_node(
    kb_name: str = Query(..., description="知识库名称"),
    node_id: str = Query(..., description="节点ID"),
):
    """
    获取节点详细信息
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        node = kg_service.get_node(node_id=node_id)

        if node:
            return BaseResponse(code=200, msg="获取节点成功", data=node)
        else:
            return BaseResponse(code=404, msg="节点不存在")

    except Exception as e:
        return BaseResponse(code=500, msg=f"获取节点时出错: {str(e)}")


@kg_router.get("/list_nodes", response_model=ListResponse, summary="列出图谱节点")
def list_nodes(
    kb_name: str = Query(..., description="知识库名称"),
    node_type: Optional[str] = Query(None, description="节点类型过滤"),
    limit: int = Query(100, description="返回数量限制"),
):
    """
    列出知识图谱中的节点
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        nodes = kg_service.list_nodes(node_type=node_type, limit=limit)

        return ListResponse(code=200, msg="获取节点列表成功", data=nodes)

    except Exception as e:
        return ListResponse(code=500, msg=f"获取节点列表时出错: {str(e)}", data=[])


@kg_router.get("/list_edges", response_model=ListResponse, summary="列出图谱边")
def list_edges(
    kb_name: str = Query(..., description="知识库名称"),
    node_id: Optional[str] = Query(None, description="节点ID过滤"),
    relation_type: Optional[str] = Query(None, description="关系类型过滤"),
    limit: int = Query(100, description="返回数量限制"),
):
    """
    列出知识图谱中的边
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        edges = kg_service.list_edges(
            node_id=node_id, relation_type=relation_type, limit=limit
        )

        return ListResponse(code=200, msg="获取边列表成功", data=edges)

    except Exception as e:
        return ListResponse(code=500, msg=f"获取边列表时出错: {str(e)}", data=[])


@kg_router.post("/update_node", response_model=BaseResponse, summary="更新节点")
def update_node(
    kb_name: str = Body(..., description="知识库名称"),
    node_id: str = Body(..., description="节点ID"),
    node_name: str = Body(..., description="节点名称"),
    node_type: Optional[str] = Body(None, description="节点类型"),
    properties: Optional[Dict] = Body(None, description="节点属性"),
):
    """
    更新节点信息（实际上是覆盖更新）
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success = kg_service.add_node(
            node_id=node_id,
            node_name=node_name,
            node_type=node_type,
            properties=properties,
        )

        if success:
            return BaseResponse(code=200, msg=f"成功更新节点 {node_name}")
        else:
            return BaseResponse(code=500, msg="更新节点失败")

    except Exception as e:
        return BaseResponse(code=500, msg=f"更新节点时出错: {str(e)}")


@kg_router.post("/update_edge", response_model=BaseResponse, summary="更新边")
def update_edge(
    kb_name: str = Body(..., description="知识库名称"),
    source_node_id: str = Body(..., description="源节点ID"),
    target_node_id: str = Body(..., description="目标节点ID"),
    relation_type: Optional[str] = Body(None, description="关系类型"),
    properties: Optional[Dict] = Body(None, description="边属性"),
    weight: float = Body(1.0, description="边权重"),
):
    """
    更新边信息（实际上是覆盖更新）
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success = kg_service.add_edge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relation_type=relation_type,
            properties=properties,
            weight=weight,
        )

        if success:
            return BaseResponse(code=200, msg=f"成功更新关系 {relation_type}")
        else:
            return BaseResponse(code=500, msg="更新关系失败")

    except Exception as e:
        return BaseResponse(code=500, msg=f"更新关系时出错: {str(e)}")


@kg_router.post("/delete_node", response_model=BaseResponse, summary="删除节点")
def delete_node(
    kb_name: str = Body(..., description="知识库名称"),
    node_id: str = Body(..., description="节点ID"),
):
    """
    删除节点（会同时删除相关的边）
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success = kg_service.delete_node(node_id=node_id)

        if success:
            return BaseResponse(code=200, msg=f"成功删除节点 {node_id}")
        else:
            return BaseResponse(code=404, msg="节点不存在或删除失败")

    except Exception as e:
        return BaseResponse(code=500, msg=f"删除节点时出错: {str(e)}")


@kg_router.post("/delete_edge", response_model=BaseResponse, summary="删除边")
def delete_edge(
    kb_name: str = Body(..., description="知识库名称"),
    edge_id: str = Body(..., description="边ID"),
):
    """
    删除边
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success = kg_service.delete_edge(edge_id=edge_id)

        if success:
            return BaseResponse(code=200, msg=f"成功删除边 {edge_id}")
        else:
            return BaseResponse(code=404, msg="边不存在或删除失败")

    except Exception as e:
        return BaseResponse(code=500, msg=f"删除边时出错: {str(e)}")


@kg_router.post("/search_nodes", response_model=ListResponse, summary="搜索节点")
def search_nodes(
    kb_name: str = Body(..., description="知识库名称"),
    keyword: str = Body(..., description="搜索关键词"),
    limit: int = Body(50, description="返回数量限制"),
):
    """
    根据关键词搜索节点
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        nodes = kg_service.search_nodes(keyword=keyword, limit=limit)

        return ListResponse(code=200, msg="搜索成功", data=nodes)

    except Exception as e:
        return ListResponse(code=500, msg=f"搜索时出错: {str(e)}", data=[])


@kg_router.get("/get_neighbors", response_model=BaseResponse, summary="获取邻居节点")
def get_neighbors(
    kb_name: str = Query(..., description="知识库名称"),
    node_id: str = Query(..., description="节点ID"),
    direction: str = Query("both", description="方向: in/out/both"),
    max_depth: int = Query(1, description="最大深度"),
):
    """
    获取节点的邻居节点和关系
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        result = kg_service.get_neighbors(
            node_id=node_id, direction=direction, max_depth=max_depth
        )

        return BaseResponse(code=200, msg="获取邻居成功", data=result)

    except Exception as e:
        return BaseResponse(code=500, msg=f"获取邻居时出错: {str(e)}")


@kg_router.get("/find_path", response_model=BaseResponse, summary="查找路径")
def find_path(
    kb_name: str = Query(..., description="知识库名称"),
    source_node_id: str = Query(..., description="源节点ID"),
    target_node_id: str = Query(..., description="目标节点ID"),
    max_length: int = Query(5, description="最大路径长度"),
):
    """
    查找两个节点之间的路径
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        paths = kg_service.find_path(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            max_length=max_length,
        )

        return BaseResponse(
            code=200, msg=f"找到 {len(paths)} 条路径", data={"paths": paths}
        )

    except Exception as e:
        return BaseResponse(code=500, msg=f"查找路径时出错: {str(e)}")


@kg_router.get("/get_stats", response_model=BaseResponse, summary="获取图谱统计")
def get_stats(
    kb_name: str = Query(..., description="知识库名称"),
):
    """
    获取知识图谱的统计信息
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        stats = kg_service.get_stats()

        return BaseResponse(code=200, msg="获取统计信息成功", data=stats)

    except Exception as e:
        return BaseResponse(code=500, msg=f"获取统计信息时出错: {str(e)}")


@kg_router.post("/clear_graph", response_model=BaseResponse, summary="清空图谱")
def clear_graph(
    kb_name: str = Body(..., description="知识库名称"),
):
    """
    清空知识库的所有图谱数据
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success = kg_service.clear_graph()

        if success:
            return BaseResponse(code=200, msg=f"成功清空知识图谱 {kb_name}")
        else:
            return BaseResponse(code=500, msg="清空图谱失败")

    except Exception as e:
        return BaseResponse(code=500, msg=f"清空图谱时出错: {str(e)}")


@kg_router.get("/export_graph", response_model=BaseResponse, summary="导出图谱")
def export_graph(
    kb_name: str = Query(..., description="知识库名称"),
):
    """
    导出知识图谱数据（JSON格式）
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        graph_data = kg_service.export_graph()

        return BaseResponse(code=200, msg="导出图谱成功", data=graph_data)

    except Exception as e:
        return BaseResponse(code=500, msg=f"导出图谱时出错: {str(e)}")


@kg_router.post("/import_graph", response_model=BaseResponse, summary="导入图谱")
def import_graph(
    kb_name: str = Body(..., description="知识库名称"),
    graph_data: Dict = Body(..., description="图谱数据"),
    clear_existing: bool = Body(False, description="是否清空现有数据"),
):
    """
    导入知识图谱数据
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success = kg_service.import_graph(
            graph_data=graph_data, clear_existing=clear_existing
        )

        if success:
            return BaseResponse(code=200, msg=f"成功导入图谱数据到 {kb_name}")
        else:
            return BaseResponse(code=500, msg="导入图谱失败")

    except Exception as e:
        return BaseResponse(code=500, msg=f"导入图谱时出错: {str(e)}")


@kg_router.post(
    "/batch_create_nodes", response_model=BaseResponse, summary="批量创建节点"
)
def batch_create_nodes(
    kb_name: str = Body(..., description="知识库名称"),
    nodes: List[Dict] = Body(..., description="节点列表"),
):
    """
    批量创建节点
    每个节点应包含: node_id, node_name, node_type(可选), properties(可选)
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success_count = 0
        failed_count = 0

        for node in nodes:
            success = kg_service.add_node(
                node_id=node["node_id"],
                node_name=node["node_name"],
                node_type=node.get("node_type"),
                properties=node.get("properties"),
            )
            if success:
                success_count += 1
            else:
                failed_count += 1

        return BaseResponse(
            code=200,
            msg=f"批量创建完成: 成功 {success_count} 个, 失败 {failed_count} 个",
        )

    except Exception as e:
        return BaseResponse(code=500, msg=f"批量创建节点时出错: {str(e)}")


@kg_router.post("/batch_create_edges", response_model=BaseResponse, summary="批量创建边")
def batch_create_edges(
    kb_name: str = Body(..., description="知识库名称"),
    edges: List[Dict] = Body(..., description="边列表"),
):
    """
    批量创建边
    每条边应包含: source_node_id, target_node_id, relation_type(可选), properties(可选), weight(可选)
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        success_count = 0
        failed_count = 0

        for edge in edges:
            success = kg_service.add_edge(
                source_node_id=edge["source_node_id"],
                target_node_id=edge["target_node_id"],
                relation_type=edge.get("relation_type"),
                properties=edge.get("properties"),
                weight=edge.get("weight", 1.0),
            )
            if success:
                success_count += 1
            else:
                failed_count += 1

        return BaseResponse(
            code=200,
            msg=f"批量创建完成: 成功 {success_count} 个, 失败 {failed_count} 个",
        )

    except Exception as e:
        return BaseResponse(code=500, msg=f"批量创建边时出错: {str(e)}")


@kg_router.post(
    "/get_context_for_llm", response_model=BaseResponse, summary="获取LLM上下文"
)
def get_context_for_llm(
    kb_name: str = Body(..., description="知识库名称"),
    query: str = Body(..., description="查询内容"),
    top_k: int = Body(10, description="返回相关节点数量"),
):
    """
    根据查询从知识图谱中提取相关上下文，供LLM使用
    这个接口是为后续LLM问答集成准备的
    """
    try:
        kg_service = KnowledgeGraphService(kb_name=kb_name)
        context = kg_service.get_graph_context_for_llm(query=query, top_k=top_k)

        return BaseResponse(code=200, msg="获取上下文成功", data={"context": context})

    except Exception as e:
        return BaseResponse(code=500, msg=f"获取上下文时出错: {str(e)}")


# 对话相关接口
kg_router.post(
    "/chat", 
    summary="知识图谱对话（使用LLM）",
    description="基于知识图谱的对话接口，将图谱信息作为上下文提供给LLM"
)(kg_chat)

kg_router.post(
    "/query", 
    response_model=BaseResponse,
    summary="简单图谱查询（不使用LLM）",
    description="直接查询知识图谱，返回相关节点和关系"
)(simple_kg_query)
