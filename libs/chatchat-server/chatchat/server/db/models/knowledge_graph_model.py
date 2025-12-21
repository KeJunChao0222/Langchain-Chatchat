from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from chatchat.server.db.base import Base


class KnowledgeGraphNodeModel(Base):
    """
    知识图谱节点模型
    """

    __tablename__ = "knowledge_graph_node"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="节点ID")
    kb_name = Column(String(50), index=True, comment="所属知识库名称")
    node_id = Column(String(100), index=True, comment="节点唯一标识")
    node_type = Column(String(50), comment="节点类型")
    node_name = Column(String(200), comment="节点名称")
    properties = Column(Text, comment="节点属性(JSON格式)")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<KnowledgeGraphNode(id='{self.id}', kb_name='{self.kb_name}', node_id='{self.node_id}', node_type='{self.node_type}', node_name='{self.node_name}')>"


class KnowledgeGraphEdgeModel(Base):
    """
    知识图谱边模型
    """

    __tablename__ = "knowledge_graph_edge"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="边ID")
    kb_name = Column(String(50), index=True, comment="所属知识库名称")
    edge_id = Column(String(100), index=True, comment="边唯一标识")
    source_node_id = Column(String(100), index=True, comment="源节点ID")
    target_node_id = Column(String(100), index=True, comment="目标节点ID")
    relation_type = Column(String(50), comment="关系类型")
    properties = Column(Text, comment="边属性(JSON格式)")
    weight = Column(Float, default=1.0, comment="边权重")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<KnowledgeGraphEdge(id='{self.id}', kb_name='{self.kb_name}', edge_id='{self.edge_id}', source='{self.source_node_id}', target='{self.target_node_id}', relation='{self.relation_type}')>"


# Pydantic Schemas
class KnowledgeGraphNodeSchema(BaseModel):
    id: int
    kb_name: str
    node_id: str
    node_type: Optional[str] = None
    node_name: str
    properties: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeGraphEdgeSchema(BaseModel):
    id: int
    kb_name: str
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation_type: Optional[str] = None
    properties: Optional[str] = None
    weight: float = 1.0
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True
