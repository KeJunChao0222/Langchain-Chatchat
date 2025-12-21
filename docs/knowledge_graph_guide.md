# 知识图谱功能使用指南

## 概述

知识图谱功能为Langchain-Chatchat增加了结构化知识管理能力，可以构建、管理和查询实体及其关系，并在LLM问答过程中提供图谱知识作为外部上下文。

## 功能特性

### 核心功能
- ✅ **节点管理**：创建、查询、更新、删除图谱节点
- ✅ **关系管理**：创建、查询、更新、删除节点间的关系（边）
- ✅ **图谱查询**：搜索节点、获取邻居、查找路径
- ✅ **批量操作**：批量创建节点和关系
- ✅ **导入导出**：支持图谱数据的JSON格式导入导出
- ✅ **LLM集成**：基于知识图谱的智能问答

### 数据模型

#### 节点（Node）
- `node_id`: 节点唯一标识
- `node_name`: 节点名称
- `node_type`: 节点类型（可选）
- `properties`: 节点属性（JSON格式，可选）
- `kb_name`: 所属知识库

#### 边（Edge）
- `edge_id`: 边唯一标识
- `source_node_id`: 源节点ID
- `target_node_id`: 目标节点ID
- `relation_type`: 关系类型（可选）
- `properties`: 边属性（JSON格式，可选）
- `weight`: 边权重（默认1.0）
- `kb_name`: 所属知识库

## API接口说明

### 基础操作

#### 1. 创建节点
```bash
POST /knowledge_graph/create_node
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "node_id": "person_001",
  "node_name": "张三",
  "node_type": "Person",
  "properties": {
    "age": 30,
    "gender": "male",
    "occupation": "工程师"
  }
}
```

#### 2. 创建关系
```bash
POST /knowledge_graph/create_edge
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "source_node_id": "person_001",
  "target_node_id": "person_002",
  "relation_type": "knows",
  "properties": {
    "since": "2020-01-01",
    "relationship": "同事"
  },
  "weight": 1.0
}
```

#### 3. 获取节点信息
```bash
GET /knowledge_graph/get_node?kb_name=test_kb&node_id=person_001
```

#### 4. 列出节点
```bash
GET /knowledge_graph/list_nodes?kb_name=test_kb&node_type=Person&limit=100
```

#### 5. 列出边
```bash
GET /knowledge_graph/list_edges?kb_name=test_kb&node_id=person_001&limit=100
```

#### 6. 搜索节点
```bash
POST /knowledge_graph/search_nodes
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "keyword": "张三",
  "limit": 50
}
```

#### 7. 更新节点
```bash
POST /knowledge_graph/update_node
```

请求体示例（同创建节点）

#### 8. 删除节点
```bash
POST /knowledge_graph/delete_node
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "node_id": "person_001"
}
```

### 高级功能

#### 1. 获取邻居节点
```bash
GET /knowledge_graph/get_neighbors?kb_name=test_kb&node_id=person_001&direction=both&max_depth=2
```

参数说明：
- `direction`: 方向（in/out/both）
- `max_depth`: 最大深度

#### 2. 查找路径
```bash
GET /knowledge_graph/find_path?kb_name=test_kb&source_node_id=person_001&target_node_id=person_002&max_length=5
```

#### 3. 获取图谱统计
```bash
GET /knowledge_graph/get_stats?kb_name=test_kb
```

返回示例：
```json
{
  "code": 200,
  "msg": "获取统计信息成功",
  "data": {
    "node_count": 100,
    "edge_count": 250
  }
}
```

#### 4. 批量创建节点
```bash
POST /knowledge_graph/batch_create_nodes
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "nodes": [
    {
      "node_id": "person_001",
      "node_name": "张三",
      "node_type": "Person"
    },
    {
      "node_id": "person_002",
      "node_name": "李四",
      "node_type": "Person"
    }
  ]
}
```

#### 5. 批量创建边
```bash
POST /knowledge_graph/batch_create_edges
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "edges": [
    {
      "source_node_id": "person_001",
      "target_node_id": "person_002",
      "relation_type": "knows"
    },
    {
      "source_node_id": "person_002",
      "target_node_id": "person_003",
      "relation_type": "friend"
    }
  ]
}
```

### 导入导出

#### 1. 导出图谱
```bash
GET /knowledge_graph/export_graph?kb_name=test_kb
```

返回JSON格式的图谱数据。

#### 2. 导入图谱
```bash
POST /knowledge_graph/import_graph
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "clear_existing": false,
  "graph_data": {
    "kb_name": "test_kb",
    "nodes": [...],
    "edges": [...]
  }
}
```

#### 3. 清空图谱
```bash
POST /knowledge_graph/clear_graph
```

请求体示例：
```json
{
  "kb_name": "test_kb"
}
```

### LLM集成

#### 1. 知识图谱对话（使用LLM）
```bash
POST /knowledge_graph/chat
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "query": "张三认识哪些人？",
  "top_k": 10,
  "history": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "你好！有什么可以帮助你的吗？"
    }
  ],
  "stream": true,
  "model": "gpt-3.5-turbo",
  "temperature": 0.7
}
```

该接口会：
1. 从知识图谱中搜索与query相关的节点和关系
2. 将图谱信息格式化为上下文
3. 结合历史对话和用户问题，调用LLM生成回答
4. 支持流式和非流式输出

#### 2. 简单图谱查询（不使用LLM）
```bash
POST /knowledge_graph/query
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "query": "张三",
  "top_k": 10
}
```

直接返回与查询相关的节点和边，不经过LLM处理。

#### 3. 获取LLM上下文
```bash
POST /knowledge_graph/get_context_for_llm
```

请求体示例：
```json
{
  "kb_name": "test_kb",
  "query": "张三的朋友",
  "top_k": 10
}
```

返回格式化的知识图谱上下文，可用于自定义LLM调用。

## 使用示例

### 示例1：构建人物关系图谱

```python
import requests

base_url = "http://localhost:7861"
kb_name = "social_network"

# 1. 创建人物节点
persons = [
    {"node_id": "p001", "node_name": "张三", "node_type": "Person", 
     "properties": {"age": 30, "city": "北京"}},
    {"node_id": "p002", "node_name": "李四", "node_type": "Person", 
     "properties": {"age": 28, "city": "上海"}},
    {"node_id": "p003", "node_name": "王五", "node_type": "Person", 
     "properties": {"age": 32, "city": "北京"}},
]

response = requests.post(
    f"{base_url}/knowledge_graph/batch_create_nodes",
    json={"kb_name": kb_name, "nodes": persons}
)
print(response.json())

# 2. 创建关系
relations = [
    {"source_node_id": "p001", "target_node_id": "p002", 
     "relation_type": "friend", "properties": {"since": "2015"}},
    {"source_node_id": "p001", "target_node_id": "p003", 
     "relation_type": "colleague", "properties": {"company": "ABC公司"}},
    {"source_node_id": "p002", "target_node_id": "p003", 
     "relation_type": "knows"},
]

response = requests.post(
    f"{base_url}/knowledge_graph/batch_create_edges",
    json={"kb_name": kb_name, "edges": relations}
)
print(response.json())

# 3. 查询张三的社交关系
response = requests.get(
    f"{base_url}/knowledge_graph/get_neighbors",
    params={"kb_name": kb_name, "node_id": "p001", "direction": "both", "max_depth": 1}
)
print(response.json())
```

### 示例2：基于图谱的智能问答

```python
import requests

base_url = "http://localhost:7861"
kb_name = "social_network"

# 使用知识图谱进行对话
response = requests.post(
    f"{base_url}/knowledge_graph/chat",
    json={
        "kb_name": kb_name,
        "query": "张三认识哪些人？他们都在哪里工作？",
        "top_k": 10,
        "stream": False,
        "model": "gpt-3.5-turbo"
    },
    stream=True
)

# 处理流式响应
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### 示例3：导出和备份图谱

```python
import requests
import json

base_url = "http://localhost:7861"
kb_name = "social_network"

# 导出图谱
response = requests.get(
    f"{base_url}/knowledge_graph/export_graph",
    params={"kb_name": kb_name}
)

graph_data = response.json()["data"]

# 保存到文件
with open("graph_backup.json", "w", encoding="utf-8") as f:
    json.dump(graph_data, f, ensure_ascii=False, indent=2)

print("图谱已导出到 graph_backup.json")

# 导入到另一个知识库
with open("graph_backup.json", "r", encoding="utf-8") as f:
    graph_data = json.load(f)

response = requests.post(
    f"{base_url}/knowledge_graph/import_graph",
    json={
        "kb_name": "new_kb",
        "clear_existing": True,
        "graph_data": graph_data
    }
)
print(response.json())
```

## 最佳实践

### 1. 节点ID设计
- 使用有意义的前缀：`person_001`, `company_abc`
- 确保唯一性
- 避免特殊字符

### 2. 关系类型命名
- 使用动词形式：`knows`, `works_at`, `located_in`
- 保持一致性
- 使用小写加下划线

### 3. 属性设计
- 使用简单的JSON可序列化类型
- 避免嵌套过深
- 合理使用类型标注

### 4. 性能优化
- 使用批量操作创建大量节点和边
- 合理设置查询limit
- 对大图进行分区管理

### 5. 与LLM集成
- top_k设置在5-20之间较为合理
- 定期清理无用的历史对话
- 使用合适的temperature参数

## 注意事项

1. **数据库初始化**：首次使用前需要运行 `chatchat-config --create-tables` 创建数据库表
2. **知识库名称**：必须与现有知识库关联，或创建新的知识库
3. **并发安全**：在高并发场景下注意数据一致性
4. **数据备份**：定期使用导出功能备份图谱数据
5. **清空操作**：清空图谱是不可逆操作，请谨慎使用

## 故障排查

### 问题1：无法创建表
**解决方案**：运行数据库初始化命令
```bash
chatchat-config --create-tables
```

### 问题2：节点创建失败
**可能原因**：
- 节点ID已存在
- JSON属性格式错误
- 知识库不存在

**解决方案**：检查请求参数，确认知识库已创建

### 问题3：LLM对话无响应
**可能原因**：
- 模型配置错误
- 知识库为空
- 网络连接问题

**解决方案**：
1. 检查模型配置
2. 确认图谱中有数据
3. 查看日志输出

## 扩展开发

### 自定义图谱处理
可以继承 `KnowledgeGraphService` 类实现自定义逻辑：

```python
from chatchat.server.knowledge_base.kg_service import KnowledgeGraphService

class CustomKGService(KnowledgeGraphService):
    def custom_analysis(self):
        # 自定义分析逻辑
        pass
```

### 集成其他图数据库
当前实现使用SQLite存储，可以扩展支持Neo4j等专业图数据库。

## 未来规划

- [ ] 支持Neo4j等专业图数据库
- [ ] 可视化界面
- [ ] 自动从文档构建图谱
- [ ] 图谱推理和规则引擎
- [ ] 多模态图谱支持

## 相关资源

- [API文档](http://localhost:7861/docs)
- [项目GitHub](https://github.com/chatchat-space/Langchain-Chatchat)
- [问题反馈](https://github.com/chatchat-space/Langchain-Chatchat/issues)
