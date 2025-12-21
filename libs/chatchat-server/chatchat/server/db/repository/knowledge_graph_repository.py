import json
from typing import Dict, List, Optional

from sqlalchemy import and_, or_

from chatchat.server.db.models.knowledge_graph_model import (
    KnowledgeGraphEdgeModel,
    KnowledgeGraphEdgeSchema,
    KnowledgeGraphNodeModel,
    KnowledgeGraphNodeSchema,
)
from chatchat.server.db.session import with_session


# Node operations
@with_session
def add_node_to_db(
    session,
    kb_name: str,
    node_id: str,
    node_name: str,
    node_type: Optional[str] = None,
    properties: Optional[Dict] = None,
):
    """添加节点到数据库"""
    node = (
        session.query(KnowledgeGraphNodeModel)
        .filter(
            and_(
                KnowledgeGraphNodeModel.kb_name == kb_name,
                KnowledgeGraphNodeModel.node_id == node_id,
            )
        )
        .first()
    )

    properties_str = json.dumps(properties, ensure_ascii=False) if properties else None

    if not node:
        node = KnowledgeGraphNodeModel(
            kb_name=kb_name,
            node_id=node_id,
            node_name=node_name,
            node_type=node_type,
            properties=properties_str,
        )
        session.add(node)
    else:
        # 更新现有节点
        node.node_name = node_name
        node.node_type = node_type
        node.properties = properties_str

    session.commit()
    return True


@with_session
def get_node_from_db(session, kb_name: str, node_id: str):
    """从数据库获取节点"""
    node = (
        session.query(KnowledgeGraphNodeModel)
        .filter(
            and_(
                KnowledgeGraphNodeModel.kb_name == kb_name,
                KnowledgeGraphNodeModel.node_id == node_id,
            )
        )
        .first()
    )
    if node:
        return KnowledgeGraphNodeSchema.model_validate(node)
    return None


@with_session
def list_nodes_from_db(
    session, kb_name: str, node_type: Optional[str] = None, limit: int = 100
):
    """列出知识库中的节点"""
    query = session.query(KnowledgeGraphNodeModel).filter(
        KnowledgeGraphNodeModel.kb_name == kb_name
    )

    if node_type:
        query = query.filter(KnowledgeGraphNodeModel.node_type == node_type)

    nodes = query.limit(limit).all()
    return [KnowledgeGraphNodeSchema.model_validate(node) for node in nodes]


@with_session
def delete_node_from_db(session, kb_name: str, node_id: str):
    """删除节点"""
    # 先删除相关的边
    session.query(KnowledgeGraphEdgeModel).filter(
        and_(
            KnowledgeGraphEdgeModel.kb_name == kb_name,
            or_(
                KnowledgeGraphEdgeModel.source_node_id == node_id,
                KnowledgeGraphEdgeModel.target_node_id == node_id,
            ),
        )
    ).delete()

    # 删除节点
    result = (
        session.query(KnowledgeGraphNodeModel)
        .filter(
            and_(
                KnowledgeGraphNodeModel.kb_name == kb_name,
                KnowledgeGraphNodeModel.node_id == node_id,
            )
        )
        .delete()
    )

    session.commit()
    return result > 0


@with_session
def search_nodes_from_db(session, kb_name: str, keyword: str, limit: int = 50):
    """搜索节点"""
    nodes = (
        session.query(KnowledgeGraphNodeModel)
        .filter(
            and_(
                KnowledgeGraphNodeModel.kb_name == kb_name,
                or_(
                    KnowledgeGraphNodeModel.node_name.like(f"%{keyword}%"),
                    KnowledgeGraphNodeModel.node_type.like(f"%{keyword}%"),
                ),
            )
        )
        .limit(limit)
        .all()
    )
    return [KnowledgeGraphNodeSchema.model_validate(node) for node in nodes]


# Edge operations
@with_session
def add_edge_to_db(
    session,
    kb_name: str,
    edge_id: str,
    source_node_id: str,
    target_node_id: str,
    relation_type: Optional[str] = None,
    properties: Optional[Dict] = None,
    weight: float = 1.0,
):
    """添加边到数据库"""
    edge = (
        session.query(KnowledgeGraphEdgeModel)
        .filter(
            and_(
                KnowledgeGraphEdgeModel.kb_name == kb_name,
                KnowledgeGraphEdgeModel.edge_id == edge_id,
            )
        )
        .first()
    )

    properties_str = json.dumps(properties, ensure_ascii=False) if properties else None

    if not edge:
        edge = KnowledgeGraphEdgeModel(
            kb_name=kb_name,
            edge_id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relation_type=relation_type,
            properties=properties_str,
            weight=weight,
        )
        session.add(edge)
    else:
        # 更新现有边
        edge.source_node_id = source_node_id
        edge.target_node_id = target_node_id
        edge.relation_type = relation_type
        edge.properties = properties_str
        edge.weight = weight

    session.commit()
    return True


@with_session
def get_edge_from_db(session, kb_name: str, edge_id: str):
    """从数据库获取边"""
    edge = (
        session.query(KnowledgeGraphEdgeModel)
        .filter(
            and_(
                KnowledgeGraphEdgeModel.kb_name == kb_name,
                KnowledgeGraphEdgeModel.edge_id == edge_id,
            )
        )
        .first()
    )
    if edge:
        return KnowledgeGraphEdgeSchema.model_validate(edge)
    return None


@with_session
def list_edges_from_db(
    session,
    kb_name: str,
    node_id: Optional[str] = None,
    relation_type: Optional[str] = None,
    limit: int = 100,
):
    """列出知识库中的边"""
    query = session.query(KnowledgeGraphEdgeModel).filter(
        KnowledgeGraphEdgeModel.kb_name == kb_name
    )

    if node_id:
        query = query.filter(
            or_(
                KnowledgeGraphEdgeModel.source_node_id == node_id,
                KnowledgeGraphEdgeModel.target_node_id == node_id,
            )
        )

    if relation_type:
        query = query.filter(KnowledgeGraphEdgeModel.relation_type == relation_type)

    edges = query.limit(limit).all()
    return [KnowledgeGraphEdgeSchema.model_validate(edge) for edge in edges]


@with_session
def delete_edge_from_db(session, kb_name: str, edge_id: str):
    """删除边"""
    result = (
        session.query(KnowledgeGraphEdgeModel)
        .filter(
            and_(
                KnowledgeGraphEdgeModel.kb_name == kb_name,
                KnowledgeGraphEdgeModel.edge_id == edge_id,
            )
        )
        .delete()
    )

    session.commit()
    return result > 0


@with_session
def clear_graph_from_db(session, kb_name: str):
    """清空知识库的所有图谱数据"""
    session.query(KnowledgeGraphEdgeModel).filter(
        KnowledgeGraphEdgeModel.kb_name == kb_name
    ).delete()
    session.query(KnowledgeGraphNodeModel).filter(
        KnowledgeGraphNodeModel.kb_name == kb_name
    ).delete()

    session.commit()
    return True


@with_session
def get_graph_stats(session, kb_name: str):
    """获取图谱统计信息"""
    node_count = (
        session.query(KnowledgeGraphNodeModel)
        .filter(KnowledgeGraphNodeModel.kb_name == kb_name)
        .count()
    )

    edge_count = (
        session.query(KnowledgeGraphEdgeModel)
        .filter(KnowledgeGraphEdgeModel.kb_name == kb_name)
        .count()
    )

    return {"node_count": node_count, "edge_count": edge_count}
