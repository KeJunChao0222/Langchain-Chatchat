"""
知识图谱服务层
提供图谱的构建、查询、编辑、保存等功能
"""
import json
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from chatchat.server.db.repository.knowledge_graph_repository import (
    add_edge_to_db,
    add_node_to_db,
    clear_graph_from_db,
    delete_edge_from_db,
    delete_node_from_db,
    get_edge_from_db,
    get_graph_stats,
    get_node_from_db,
    list_edges_from_db,
    list_nodes_from_db,
    search_nodes_from_db,
)
from chatchat.utils import build_logger

logger = build_logger()


class KnowledgeGraphService:
    """知识图谱服务类"""

    def __init__(self, kb_name: str):
        self.kb_name = kb_name
        self.graph = nx.DiGraph()  # 有向图

    def add_node(
        self,
        node_id: str,
        node_name: str,
        node_type: Optional[str] = None,
        properties: Optional[Dict] = None,
    ) -> bool:
        """添加节点"""
        try:
            # 添加到networkx图
            self.graph.add_node(
                node_id, name=node_name, node_type=node_type, **(properties or {})
            )

            # 保存到数据库
            add_node_to_db(
                kb_name=self.kb_name,
                node_id=node_id,
                node_name=node_name,
                node_type=node_type,
                properties=properties,
            )

            logger.info(
                f"Added node: {node_id} ({node_name}) to knowledge graph {self.kb_name}"
            )
            return True
        except Exception as e:
            logger.error(f"Error adding node: {e}")
            return False

    def add_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        relation_type: Optional[str] = None,
        properties: Optional[Dict] = None,
        weight: float = 1.0,
    ) -> bool:
        """添加边"""
        try:
            edge_id = f"{source_node_id}_{relation_type}_{target_node_id}"

            # 添加到networkx图
            self.graph.add_edge(
                source_node_id,
                target_node_id,
                relation_type=relation_type,
                weight=weight,
                **(properties or {}),
            )

            # 保存到数据库
            add_edge_to_db(
                kb_name=self.kb_name,
                edge_id=edge_id,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                relation_type=relation_type,
                properties=properties,
                weight=weight,
            )

            logger.info(
                f"Added edge: {source_node_id} -> {target_node_id} ({relation_type})"
            )
            return True
        except Exception as e:
            logger.error(f"Error adding edge: {e}")
            return False

    def get_node(self, node_id: str) -> Optional[Dict]:
        """获取节点信息"""
        node = get_node_from_db(kb_name=self.kb_name, node_id=node_id)
        if node:
            result = node.model_dump()
            if result.get("properties"):
                try:
                    result["properties"] = json.loads(result["properties"])
                except:
                    pass
            return result
        return None

    def get_edge(self, edge_id: str) -> Optional[Dict]:
        """获取边信息"""
        edge = get_edge_from_db(kb_name=self.kb_name, edge_id=edge_id)
        if edge:
            result = edge.model_dump()
            if result.get("properties"):
                try:
                    result["properties"] = json.loads(result["properties"])
                except:
                    pass
            return result
        return None

    def list_nodes(
        self, node_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """列出节点"""
        nodes = list_nodes_from_db(
            kb_name=self.kb_name, node_type=node_type, limit=limit
        )
        result = []
        for node in nodes:
            node_dict = node.model_dump()
            if node_dict.get("properties"):
                try:
                    node_dict["properties"] = json.loads(node_dict["properties"])
                except:
                    pass
            result.append(node_dict)
        return result

    def list_edges(
        self,
        node_id: Optional[str] = None,
        relation_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """列出边"""
        edges = list_edges_from_db(
            kb_name=self.kb_name,
            node_id=node_id,
            relation_type=relation_type,
            limit=limit,
        )
        result = []
        for edge in edges:
            edge_dict = edge.model_dump()
            if edge_dict.get("properties"):
                try:
                    edge_dict["properties"] = json.loads(edge_dict["properties"])
                except:
                    pass
            result.append(edge_dict)
        return result

    def delete_node(self, node_id: str) -> bool:
        """删除节点（同时删除相关的边）"""
        try:
            # 从networkx图中删除
            if self.graph.has_node(node_id):
                self.graph.remove_node(node_id)

            # 从数据库删除
            delete_node_from_db(kb_name=self.kb_name, node_id=node_id)

            logger.info(f"Deleted node: {node_id} from knowledge graph {self.kb_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting node: {e}")
            return False

    def delete_edge(self, edge_id: str) -> bool:
        """删除边"""
        try:
            # 从数据库获取边信息
            edge = get_edge_from_db(kb_name=self.kb_name, edge_id=edge_id)
            if edge:
                # 从networkx图中删除
                if self.graph.has_edge(edge.source_node_id, edge.target_node_id):
                    self.graph.remove_edge(edge.source_node_id, edge.target_node_id)

                # 从数据库删除
                delete_edge_from_db(kb_name=self.kb_name, edge_id=edge_id)

                logger.info(f"Deleted edge: {edge_id} from knowledge graph {self.kb_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting edge: {e}")
            return False

    def search_nodes(self, keyword: str, limit: int = 50) -> List[Dict]:
        """搜索节点"""
        nodes = search_nodes_from_db(
            kb_name=self.kb_name, keyword=keyword, limit=limit
        )
        result = []
        for node in nodes:
            node_dict = node.model_dump()
            if node_dict.get("properties"):
                try:
                    node_dict["properties"] = json.loads(node_dict["properties"])
                except:
                    pass
            result.append(node_dict)
        return result

    def get_neighbors(
        self, node_id: str, direction: str = "both", max_depth: int = 1
    ) -> Dict[str, Any]:
        """获取节点的邻居
        
        Args:
            node_id: 节点ID
            direction: 方向 ('in', 'out', 'both')
            max_depth: 最大深度
        """
        result = {"nodes": [], "edges": []}

        try:
            # 加载相关的图数据
            self._load_subgraph(node_id, max_depth)

            visited_nodes = set()
            visited_edges = set()

            def _traverse(current_id: str, depth: int):
                if depth > max_depth or current_id in visited_nodes:
                    return

                visited_nodes.add(current_id)
                node_info = self.get_node(current_id)
                if node_info:
                    result["nodes"].append(node_info)

                if depth < max_depth:
                    # 获取出边
                    if direction in ["out", "both"]:
                        edges = list_edges_from_db(
                            kb_name=self.kb_name, node_id=current_id, limit=100
                        )
                        for edge in edges:
                            if edge.source_node_id == current_id:
                                edge_dict = edge.model_dump()
                                if edge_dict.get("properties"):
                                    try:
                                        edge_dict["properties"] = json.loads(
                                            edge_dict["properties"]
                                        )
                                    except:
                                        pass
                                
                                edge_key = (edge.source_node_id, edge.target_node_id, edge.relation_type)
                                if edge_key not in visited_edges:
                                    visited_edges.add(edge_key)
                                    result["edges"].append(edge_dict)
                                    _traverse(edge.target_node_id, depth + 1)

                    # 获取入边
                    if direction in ["in", "both"]:
                        edges = list_edges_from_db(
                            kb_name=self.kb_name, node_id=current_id, limit=100
                        )
                        for edge in edges:
                            if edge.target_node_id == current_id:
                                edge_dict = edge.model_dump()
                                if edge_dict.get("properties"):
                                    try:
                                        edge_dict["properties"] = json.loads(
                                            edge_dict["properties"]
                                        )
                                    except:
                                        pass
                                
                                edge_key = (edge.source_node_id, edge.target_node_id, edge.relation_type)
                                if edge_key not in visited_edges:
                                    visited_edges.add(edge_key)
                                    result["edges"].append(edge_dict)
                                    _traverse(edge.source_node_id, depth + 1)

            _traverse(node_id, 0)

        except Exception as e:
            logger.error(f"Error getting neighbors: {e}")

        return result

    def _load_subgraph(self, node_id: str, depth: int):
        """加载子图到networkx"""
        # 这里可以优化，只加载需要的部分
        pass

    def clear_graph(self) -> bool:
        """清空图谱"""
        try:
            self.graph.clear()
            clear_graph_from_db(kb_name=self.kb_name)
            logger.info(f"Cleared knowledge graph {self.kb_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            return False

    def get_stats(self) -> Dict[str, int]:
        """获取图谱统计信息"""
        return get_graph_stats(kb_name=self.kb_name)

    def export_graph(self) -> Dict[str, Any]:
        """导出图谱数据"""
        nodes = self.list_nodes(limit=10000)
        edges = self.list_edges(limit=10000)

        return {"kb_name": self.kb_name, "nodes": nodes, "edges": edges}

    def import_graph(self, graph_data: Dict[str, Any], clear_existing: bool = False):
        """导入图谱数据"""
        try:
            if clear_existing:
                self.clear_graph()

            # 导入节点
            for node in graph_data.get("nodes", []):
                self.add_node(
                    node_id=node["node_id"],
                    node_name=node["node_name"],
                    node_type=node.get("node_type"),
                    properties=node.get("properties"),
                )

            # 导入边
            for edge in graph_data.get("edges", []):
                self.add_edge(
                    source_node_id=edge["source_node_id"],
                    target_node_id=edge["target_node_id"],
                    relation_type=edge.get("relation_type"),
                    properties=edge.get("properties"),
                    weight=edge.get("weight", 1.0),
                )

            logger.info(f"Imported graph data to {self.kb_name}")
            return True
        except Exception as e:
            logger.error(f"Error importing graph: {e}")
            return False

    def find_path(
        self, source_node_id: str, target_node_id: str, max_length: int = 5
    ) -> List[List[str]]:
        """查找两个节点之间的路径"""
        try:
            # 加载相关数据到networkx
            # 这里简化处理，实际应用中需要更智能的加载策略
            nodes = self.list_nodes(limit=1000)
            edges = self.list_edges(limit=1000)

            # 构建临时图
            temp_graph = nx.DiGraph()
            for node in nodes:
                temp_graph.add_node(node["node_id"])
            for edge in edges:
                temp_graph.add_edge(edge["source_node_id"], edge["target_node_id"])

            # 查找所有简单路径
            paths = []
            try:
                all_paths = nx.all_simple_paths(
                    temp_graph,
                    source_node_id,
                    target_node_id,
                    cutoff=max_length,
                )
                paths = list(all_paths)
            except nx.NetworkXNoPath:
                pass

            return paths
        except Exception as e:
            logger.error(f"Error finding path: {e}")
            return []

    def get_graph_context_for_llm(
        self, query: str, top_k: int = 10
    ) -> str:
        """为LLM生成图谱上下文
        
        根据查询关键词，从知识图谱中提取相关的节点和关系，
        格式化为LLM可理解的文本上下文
        """
        try:
            # 搜索相关节点
            nodes = self.search_nodes(keyword=query, limit=top_k)

            if not nodes:
                return ""

            # 构建上下文文本
            context_parts = ["# 知识图谱上下文\n"]

            for node in nodes:
                # 添加节点信息
                context_parts.append(
                    f"## 实体: {node['node_name']} ({node.get('node_type', '未分类')})"
                )

                if node.get("properties"):
                    context_parts.append("属性:")
                    for key, value in node["properties"].items():
                        context_parts.append(f"  - {key}: {value}")

                # 获取相关边
                edges = self.list_edges(node_id=node["node_id"], limit=20)

                if edges:
                    context_parts.append("关系:")
                    for edge in edges:
                        if edge["source_node_id"] == node["node_id"]:
                            # 出边
                            target = self.get_node(edge["target_node_id"])
                            if target:
                                context_parts.append(
                                    f"  - {edge.get('relation_type', '关联')} -> {target['node_name']}"
                                )
                        else:
                            # 入边
                            source = self.get_node(edge["source_node_id"])
                            if source:
                                context_parts.append(
                                    f"  - {source['node_name']} {edge.get('relation_type', '关联')} -> {node['node_name']}"
                                )

                context_parts.append("")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error generating LLM context: {e}")
            return ""
