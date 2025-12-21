# 知识图谱功能快速入门

## 第一步：初始化数据库

在使用知识图谱功能前，需要先创建数据库表：

```bash
cd /root/Langchain-Chatchat/libs/chatchat-server
chatchat-config --create-tables
```

## 第二步：启动服务

如果服务未启动，运行：

```bash
chatchat-config
```

服务将在 `http://localhost:7861` 启动。

## 第三步：测试API

### 方式1：使用curl命令

```bash
# 1. 创建第一个节点
curl -X POST "http://localhost:7861/knowledge_graph/create_node" \
  -H "Content-Type: application/json" \
  -d '{
    "kb_name": "test_kg",
    "node_id": "person_001",
    "node_name": "张三",
    "node_type": "Person",
    "properties": {"age": 30, "city": "北京"}
  }'

# 2. 创建第二个节点
curl -X POST "http://localhost:7861/knowledge_graph/create_node" \
  -H "Content-Type: application/json" \
  -d '{
    "kb_name": "test_kg",
    "node_id": "person_002",
    "node_name": "李四",
    "node_type": "Person",
    "properties": {"age": 28, "city": "上海"}
  }'

# 3. 创建关系
curl -X POST "http://localhost:7861/knowledge_graph/create_edge" \
  -H "Content-Type: application/json" \
  -d '{
    "kb_name": "test_kg",
    "source_node_id": "person_001",
    "target_node_id": "person_002",
    "relation_type": "knows",
    "properties": {"since": "2020"}
  }'

# 4. 查询节点
curl -X GET "http://localhost:7861/knowledge_graph/list_nodes?kb_name=test_kg&limit=10"

# 5. 搜索节点
curl -X POST "http://localhost:7861/knowledge_graph/search_nodes" \
  -H "Content-Type: application/json" \
  -d '{
    "kb_name": "test_kg",
    "keyword": "张三",
    "limit": 10
  }'

# 6. 获取统计信息
curl -X GET "http://localhost:7861/knowledge_graph/get_stats?kb_name=test_kg"
```

### 方式2：使用Python脚本

创建文件 `test_kg.py`：

```python
import requests

base_url = "http://localhost:7861"

# 1. 创建节点
print("1. 创建节点...")
response = requests.post(
    f"{base_url}/knowledge_graph/create_node",
    json={
        "kb_name": "test_kg",
        "node_id": "person_001",
        "node_name": "张三",
        "node_type": "Person",
        "properties": {"age": 30, "city": "北京"}
    }
)
print(response.json())

# 2. 创建关系
print("\n2. 创建关系...")
response = requests.post(
    f"{base_url}/knowledge_graph/create_edge",
    json={
        "kb_name": "test_kg",
        "source_node_id": "person_001",
        "target_node_id": "person_002",
        "relation_type": "knows"
    }
)
print(response.json())

# 3. 查询统计
print("\n3. 查询统计...")
response = requests.get(f"{base_url}/knowledge_graph/get_stats?kb_name=test_kg")
print(response.json())
```

运行脚本：
```bash
python test_kg.py
```

### 方式3：运行完整示例

```bash
cd /root/Langchain-Chatchat
python examples/knowledge_graph_example.py
```

## 第四步：查看API文档

访问 Swagger UI 查看所有API接口：

```
http://localhost:7861/docs
```

在页面中找到 "Knowledge Graph Management" 标签，可以看到所有知识图谱相关的API。

## 常用API速查

| 功能 | 方法 | 端点 |
|------|------|------|
| 创建节点 | POST | /knowledge_graph/create_node |
| 创建边 | POST | /knowledge_graph/create_edge |
| 列出节点 | GET | /knowledge_graph/list_nodes |
| 搜索节点 | POST | /knowledge_graph/search_nodes |
| 获取邻居 | GET | /knowledge_graph/get_neighbors |
| 查找路径 | GET | /knowledge_graph/find_path |
| 图谱统计 | GET | /knowledge_graph/get_stats |
| 导出图谱 | GET | /knowledge_graph/export_graph |
| 导入图谱 | POST | /knowledge_graph/import_graph |
| 图谱对话 | POST | /knowledge_graph/chat |

## 下一步

- 查看详细文档: `docs/knowledge_graph_guide.md`
- 了解更多示例: `examples/knowledge_graph_example.py`
- 查看完整功能说明: `KNOWLEDGE_GRAPH_README.md`

## 常见问题

### Q: 提示表不存在
A: 运行 `chatchat-config --create-tables` 创建数据库表

### Q: 如何清空图谱数据？
A: 使用 `POST /knowledge_graph/clear_graph` 接口

### Q: 如何备份图谱？
A: 使用 `GET /knowledge_graph/export_graph` 导出为JSON文件

### Q: 如何结合LLM使用？
A: 使用 `POST /knowledge_graph/chat` 接口，会自动提取图谱上下文供LLM使用
