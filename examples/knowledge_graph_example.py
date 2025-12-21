"""
知识图谱功能示例
演示如何使用知识图谱API构建和查询图谱
"""
import json
import requests
from typing import Dict, List


class KnowledgeGraphClient:
    """知识图谱客户端"""

    def __init__(self, base_url: str = "http://localhost:7861"):
        self.base_url = base_url
        self.kg_prefix = f"{base_url}/knowledge_graph"

    def create_node(
        self,
        kb_name: str,
        node_id: str,
        node_name: str,
        node_type: str = None,
        properties: Dict = None,
    ) -> Dict:
        """创建节点"""
        url = f"{self.kg_prefix}/create_node"
        data = {
            "kb_name": kb_name,
            "node_id": node_id,
            "node_name": node_name,
            "node_type": node_type,
            "properties": properties,
        }
        response = requests.post(url, json=data)
        return response.json()

    def create_edge(
        self,
        kb_name: str,
        source_node_id: str,
        target_node_id: str,
        relation_type: str = None,
        properties: Dict = None,
        weight: float = 1.0,
    ) -> Dict:
        """创建边"""
        url = f"{self.kg_prefix}/create_edge"
        data = {
            "kb_name": kb_name,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "relation_type": relation_type,
            "properties": properties,
            "weight": weight,
        }
        response = requests.post(url, json=data)
        return response.json()

    def batch_create_nodes(self, kb_name: str, nodes: List[Dict]) -> Dict:
        """批量创建节点"""
        url = f"{self.kg_prefix}/batch_create_nodes"
        data = {"kb_name": kb_name, "nodes": nodes}
        response = requests.post(url, json=data)
        return response.json()

    def batch_create_edges(self, kb_name: str, edges: List[Dict]) -> Dict:
        """批量创建边"""
        url = f"{self.kg_prefix}/batch_create_edges"
        data = {"kb_name": kb_name, "edges": edges}
        response = requests.post(url, json=data)
        return response.json()

    def search_nodes(self, kb_name: str, keyword: str, limit: int = 50) -> Dict:
        """搜索节点"""
        url = f"{self.kg_prefix}/search_nodes"
        data = {"kb_name": kb_name, "keyword": keyword, "limit": limit}
        response = requests.post(url, json=data)
        return response.json()

    def get_neighbors(
        self,
        kb_name: str,
        node_id: str,
        direction: str = "both",
        max_depth: int = 1,
    ) -> Dict:
        """获取邻居节点"""
        url = f"{self.kg_prefix}/get_neighbors"
        params = {
            "kb_name": kb_name,
            "node_id": node_id,
            "direction": direction,
            "max_depth": max_depth,
        }
        response = requests.get(url, params=params)
        return response.json()

    def find_path(
        self,
        kb_name: str,
        source_node_id: str,
        target_node_id: str,
        max_length: int = 5,
    ) -> Dict:
        """查找路径"""
        url = f"{self.kg_prefix}/find_path"
        params = {
            "kb_name": kb_name,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "max_length": max_length,
        }
        response = requests.get(url, params=params)
        return response.json()

    def get_stats(self, kb_name: str) -> Dict:
        """获取统计信息"""
        url = f"{self.kg_prefix}/get_stats"
        params = {"kb_name": kb_name}
        response = requests.get(url, params=params)
        return response.json()

    def export_graph(self, kb_name: str) -> Dict:
        """导出图谱"""
        url = f"{self.kg_prefix}/export_graph"
        params = {"kb_name": kb_name}
        response = requests.get(url, params=params)
        return response.json()

    def import_graph(
        self, kb_name: str, graph_data: Dict, clear_existing: bool = False
    ) -> Dict:
        """导入图谱"""
        url = f"{self.kg_prefix}/import_graph"
        data = {
            "kb_name": kb_name,
            "graph_data": graph_data,
            "clear_existing": clear_existing,
        }
        response = requests.post(url, json=data)
        return response.json()

    def kg_chat(
        self,
        kb_name: str,
        query: str,
        top_k: int = 10,
        history: List[Dict] = None,
        stream: bool = False,
    ) -> Dict:
        """知识图谱对话"""
        url = f"{self.kg_prefix}/chat"
        data = {
            "kb_name": kb_name,
            "query": query,
            "top_k": top_k,
            "history": history or [],
            "stream": stream,
        }
        response = requests.post(url, json=data, stream=stream)

        if stream:
            return response
        else:
            return response.json()

    def simple_query(self, kb_name: str, query: str, top_k: int = 10) -> Dict:
        """简单查询"""
        url = f"{self.kg_prefix}/query"
        data = {"kb_name": kb_name, "query": query, "top_k": top_k}
        response = requests.post(url, json=data)
        return response.json()


def example_1_build_company_graph():
    """示例1：构建公司组织架构图谱"""
    print("=" * 60)
    print("示例1：构建公司组织架构图谱")
    print("=" * 60)

    client = KnowledgeGraphClient()
    kb_name = "company_org"

    # 创建人员节点
    print("\n1. 创建人员节点...")
    persons = [
        {
            "node_id": "emp_001",
            "node_name": "张三",
            "node_type": "Employee",
            "properties": {"position": "CEO", "department": "管理层", "level": "高管"},
        },
        {
            "node_id": "emp_002",
            "node_name": "李四",
            "node_type": "Employee",
            "properties": {"position": "技术总监", "department": "技术部", "level": "总监"},
        },
        {
            "node_id": "emp_003",
            "node_name": "王五",
            "node_type": "Employee",
            "properties": {
                "position": "高级工程师",
                "department": "技术部",
                "level": "骨干",
            },
        },
        {
            "node_id": "emp_004",
            "node_name": "赵六",
            "node_type": "Employee",
            "properties": {"position": "产品经理", "department": "产品部", "level": "经理"},
        },
    ]

    result = client.batch_create_nodes(kb_name, persons)
    print(f"创建节点结果: {result['msg']}")

    # 创建部门节点
    print("\n2. 创建部门节点...")
    departments = [
        {
            "node_id": "dept_001",
            "node_name": "技术部",
            "node_type": "Department",
            "properties": {"location": "3楼", "headcount": 50},
        },
        {
            "node_id": "dept_002",
            "node_name": "产品部",
            "node_type": "Department",
            "properties": {"location": "2楼", "headcount": 20},
        },
    ]

    result = client.batch_create_nodes(kb_name, departments)
    print(f"创建部门节点结果: {result['msg']}")

    # 创建关系
    print("\n3. 创建组织关系...")
    relations = [
        {
            "source_node_id": "emp_001",
            "target_node_id": "emp_002",
            "relation_type": "manages",
            "properties": {"since": "2020-01"},
        },
        {
            "source_node_id": "emp_002",
            "target_node_id": "emp_003",
            "relation_type": "manages",
            "properties": {"since": "2021-03"},
        },
        {
            "source_node_id": "emp_001",
            "target_node_id": "emp_004",
            "relation_type": "manages",
            "properties": {"since": "2020-06"},
        },
        {
            "source_node_id": "emp_002",
            "target_node_id": "dept_001",
            "relation_type": "heads",
        },
        {
            "source_node_id": "emp_004",
            "target_node_id": "dept_002",
            "relation_type": "heads",
        },
        {
            "source_node_id": "emp_003",
            "target_node_id": "dept_001",
            "relation_type": "belongs_to",
        },
    ]

    result = client.batch_create_edges(kb_name, relations)
    print(f"创建关系结果: {result['msg']}")

    # 查询图谱统计
    print("\n4. 查询图谱统计...")
    stats = client.get_stats(kb_name)
    print(f"节点数量: {stats['data']['node_count']}")
    print(f"边数量: {stats['data']['edge_count']}")

    print("\n示例1完成！")


def example_2_query_graph():
    """示例2：查询图谱"""
    print("\n" + "=" * 60)
    print("示例2：查询图谱")
    print("=" * 60)

    client = KnowledgeGraphClient()
    kb_name = "company_org"

    # 搜索节点
    print("\n1. 搜索'张三'相关节点...")
    result = client.search_nodes(kb_name, "张三", limit=10)
    if result["code"] == 200:
        nodes = result["data"]
        print(f"找到 {len(nodes)} 个节点:")
        for node in nodes:
            print(f"  - {node['node_name']} ({node.get('node_type', 'N/A')})")

    # 获取邻居
    print("\n2. 获取张三的直接下属...")
    result = client.get_neighbors(kb_name, "emp_001", direction="out", max_depth=1)
    if result["code"] == 200:
        data = result["data"]
        print(f"找到 {len(data['nodes'])} 个相关节点, {len(data['edges'])} 条关系")
        for edge in data["edges"]:
            if edge["source_node_id"] == "emp_001":
                print(
                    f"  - {edge['source_node_id']} --[{edge['relation_type']}]--> {edge['target_node_id']}"
                )

    # 查找路径
    print("\n3. 查找张三到王五的路径...")
    result = client.find_path(kb_name, "emp_001", "emp_003", max_length=5)
    if result["code"] == 200:
        paths = result["data"]["paths"]
        print(f"找到 {len(paths)} 条路径:")
        for i, path in enumerate(paths, 1):
            print(f"  路径{i}: {' -> '.join(path)}")

    print("\n示例2完成！")


def example_3_kg_chat():
    """示例3：基于知识图谱的对话"""
    print("\n" + "=" * 60)
    print("示例3：基于知识图谱的对话")
    print("=" * 60)

    client = KnowledgeGraphClient()
    kb_name = "company_org"

    # 简单查询（不使用LLM）
    print("\n1. 简单查询：张三")
    result = client.simple_query(kb_name, "张三", top_k=5)
    if result["code"] == 200:
        data = result["data"]
        print(f"找到 {len(data['nodes'])} 个节点, {len(data['edges'])} 条关系")

    # LLM对话（需要配置好LLM）
    print("\n2. LLM对话：张三管理哪些人？")
    print("注意：此功能需要正确配置LLM才能使用")

    # 取消注释以下代码来测试LLM对话
    # try:
    #     result = client.kg_chat(
    #         kb_name=kb_name,
    #         query="张三管理哪些人？他们分别在哪个部门？",
    #         top_k=10,
    #         stream=False
    #     )
    #     if result["code"] == 200:
    #         print(f"LLM回答: {result['data']}")
    # except Exception as e:
    #     print(f"LLM对话失败: {e}")

    print("\n示例3完成！")


def example_4_export_import():
    """示例4：导出和导入图谱"""
    print("\n" + "=" * 60)
    print("示例4：导出和导入图谱")
    print("=" * 60)

    client = KnowledgeGraphClient()
    kb_name = "company_org"

    # 导出图谱
    print("\n1. 导出图谱...")
    result = client.export_graph(kb_name)
    if result["code"] == 200:
        graph_data = result["data"]
        print(f"导出成功！")
        print(f"节点数: {len(graph_data['nodes'])}")
        print(f"边数: {len(graph_data['edges'])}")

        # 保存到文件
        filename = f"{kb_name}_export.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        print(f"已保存到文件: {filename}")

        # 导入到新知识库
        print("\n2. 导入到新知识库 'company_org_backup'...")
        new_kb_name = "company_org_backup"
        result = client.import_graph(new_kb_name, graph_data, clear_existing=True)
        print(f"导入结果: {result['msg']}")

        # 验证导入
        print("\n3. 验证导入结果...")
        stats = client.get_stats(new_kb_name)
        print(f"新图谱节点数: {stats['data']['node_count']}")
        print(f"新图谱边数: {stats['data']['edge_count']}")

    print("\n示例4完成！")


def main():
    """主函数"""
    print("知识图谱功能示例")
    print("=" * 60)
    print("确保Chatchat服务已启动在 http://localhost:7861")
    print("=" * 60)

    try:
        # 运行示例
        example_1_build_company_graph()
        example_2_query_graph()
        example_3_kg_chat()
        example_4_export_import()

        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n错误：无法连接到服务器，请确保Chatchat服务已启动")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
