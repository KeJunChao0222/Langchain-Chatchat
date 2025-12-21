# 知识图谱功能说明

## 概述

本次更新为 Langchain-Chatchat 项目新增了完整的**知识图谱功能**，支持构建、查询、编辑、保存知识图谱，并可在LLM问答过程中提供外部知识支持。

## 新增内容

### 1. 数据库模型
- **文件**: `chatchat/server/db/models/knowledge_graph_model.py`
- **功能**: 
  - `KnowledgeGraphNodeModel`: 图谱节点模型
  - `KnowledgeGraphEdgeModel`: 图谱边（关系）模型
  - 支持节点属性、关系属性、权重等

### 2. 数据库操作层
- **文件**: `chatchat/server/db/repository/knowledge_graph_repository.py`
- **功能**:
  - 节点的增删改查
  - 边的增删改查
  - 图谱搜索、统计
  - 批量操作支持

### 3. 服务层
- **文件**: `chatchat/server/knowledge_base/kg_service.py`
- **功能**:
  - `KnowledgeGraphService`: 核心服务类
  - 图谱构建、查询、编辑
  - 路径查找、邻居获取
  - 导入导出功能
  - 为LLM生成图谱上下文

### 4. API路由
- **文件**: `chatchat/server/api_server/kg_routes.py`
- **功能**: 提供完整的REST API接口
  - 基础操作：创建、查询、更新、删除节点和边
  - 高级功能：搜索、路径查找、邻居获取、统计
  - 批量操作：批量创建节点和边
  - 数据管理：导入导出、清空图谱
  - LLM集成：知识图谱对话、上下文生成

### 5. LLM集成
- **文件**: `chatchat/server/chat/kg_chat.py`
- **功能**:
  - `kg_chat`: 基于知识图谱的LLM对话
  - `simple_kg_query`: 直接查询图谱（不使用LLM）
  - 自动从图谱中提取相关上下文供LLM使用

### 6. 文档和示例
- **文档**: `docs/knowledge_graph_guide.md` - 详细的使用指南
- **示例**: `examples/knowledge_graph_example.py` - 完整的使用示例

## 核心特性

### ✅ 已实现功能

1. **节点管理**
   - 创建、查询、更新、删除节点
   - 支持节点类型和自定义属性
   - 批量创建节点

2. **关系管理**
   - 创建、查询、更新、删除边（关系）
   - 支持关系类型、属性和权重
   - 批量创建关系

3. **图谱查询**
   - 关键词搜索节点
   - 获取节点邻居（支持方向和深度控制）
   - 查找两个节点间的路径
   - 图谱统计信息

4. **数据管理**
   - JSON格式导出整个图谱
   - 从JSON导入图谱数据
   - 清空图谱数据

5. **LLM集成** ⭐
   - 基于图谱的智能问答
   - 自动提取相关图谱上下文
   - 支持流式和非流式输出
   - 历史对话支持

## 技术栈

- **后端框架**: FastAPI
- **数据库**: SQLAlchemy (支持SQLite/PostgreSQL/MySQL)
- **图计算**: NetworkX
- **LLM集成**: Langchain

## 快速开始

### 1. 初始化数据库

首次使用需要创建数据库表：

```bash
cd /root/Langchain-Chatchat/libs/chatchat-server
chatchat-config --create-tables
```

### 2. 启动服务

```bash
chatchat-config
```

服务将在 `http://localhost:7861` 启动

### 3. 使用示例

#### Python代码示例

```python
import requests

base_url = "http://localhost:7861"
kb_name = "test_kg"

# 创建节点
response = requests.post(
    f"{base_url}/knowledge_graph/create_node",
    json={
        "kb_name": kb_name,
        "node_id": "person_001",
        "node_name": "张三",
        "node_type": "Person",
        "properties": {"age": 30, "city": "北京"}
    }
)
print(response.json())

# 创建关系
response = requests.post(
    f"{base_url}/knowledge_graph/create_edge",
    json={
        "kb_name": kb_name,
        "source_node_id": "person_001",
        "target_node_id": "person_002",
        "relation_type": "knows"
    }
)
print(response.json())

# 知识图谱对话
response = requests.post(
    f"{base_url}/knowledge_graph/chat",
    json={
        "kb_name": kb_name,
        "query": "张三认识谁？",
        "top_k": 10,
        "stream": False
    }
)
print(response.json())
```

#### 运行完整示例

```bash
cd /root/Langchain-Chatchat
python examples/knowledge_graph_example.py
```

### 4. API文档

访问 `http://localhost:7861/docs` 查看完整的API文档

## API接口列表

### 基础操作
- `POST /knowledge_graph/create_node` - 创建节点
- `POST /knowledge_graph/create_edge` - 创建边
- `GET /knowledge_graph/get_node` - 获取节点
- `GET /knowledge_graph/list_nodes` - 列出节点
- `GET /knowledge_graph/list_edges` - 列出边
- `POST /knowledge_graph/update_node` - 更新节点
- `POST /knowledge_graph/update_edge` - 更新边
- `POST /knowledge_graph/delete_node` - 删除节点
- `POST /knowledge_graph/delete_edge` - 删除边

### 高级功能
- `POST /knowledge_graph/search_nodes` - 搜索节点
- `GET /knowledge_graph/get_neighbors` - 获取邻居
- `GET /knowledge_graph/find_path` - 查找路径
- `GET /knowledge_graph/get_stats` - 获取统计
- `POST /knowledge_graph/batch_create_nodes` - 批量创建节点
- `POST /knowledge_graph/batch_create_edges` - 批量创建边

### 数据管理
- `GET /knowledge_graph/export_graph` - 导出图谱
- `POST /knowledge_graph/import_graph` - 导入图谱
- `POST /knowledge_graph/clear_graph` - 清空图谱

### LLM集成
- `POST /knowledge_graph/chat` - 知识图谱对话（使用LLM）
- `POST /knowledge_graph/query` - 简单查询（不使用LLM）
- `POST /knowledge_graph/get_context_for_llm` - 获取LLM上下文

## 应用场景

1. **企业知识管理**
   - 组织架构管理
   - 业务流程图谱
   - 产品关系图谱

2. **智能问答增强**
   - 结构化知识问答
   - 关系推理问答
   - 多跳问答

3. **数据分析**
   - 社交网络分析
   - 关系发现
   - 路径分析

4. **知识发现**
   - 实体关系抽取
   - 知识融合
   - 图谱推理

## 与现有功能的集成

知识图谱功能与现有的知识库功能互补：

| 功能 | 知识库（Knowledge Base） | 知识图谱（Knowledge Graph） |
|------|------------------------|---------------------------|
| 数据类型 | 非结构化文本 | 结构化实体和关系 |
| 检索方式 | 向量检索 | 图查询、路径搜索 |
| 适用场景 | 文档问答、语义搜索 | 关系推理、结构化问答 |
| LLM集成 | RAG（检索增强生成） | 图谱增强生成 |

**推荐用法**：
- 非结构化知识使用知识库
- 结构化关系使用知识图谱
- 结合使用可获得最佳效果

## 注意事项

1. **首次使用**: 必须先运行 `chatchat-config --create-tables` 创建数据库表
2. **知识库命名**: 图谱必须关联到一个知识库名称
3. **节点ID唯一性**: 同一知识库内节点ID必须唯一
4. **性能考虑**: 
   - 大图谱查询建议设置合理的limit
   - 批量操作优于单个操作
   - 路径查找设置合理的max_length
5. **数据备份**: 定期使用导出功能备份数据

## 代码文件清单

```
libs/chatchat-server/chatchat/
├── server/
│   ├── db/
│   │   ├── models/
│   │   │   └── knowledge_graph_model.py          # 数据模型
│   │   └── repository/
│   │       └── knowledge_graph_repository.py     # 数据库操作
│   ├── knowledge_base/
│   │   ├── kg_service.py                         # 服务层
│   │   └── migrate.py                            # 更新：导入图谱模型
│   ├── api_server/
│   │   ├── kg_routes.py                          # API路由
│   │   └── server_app.py                         # 更新：注册图谱路由
│   └── chat/
│       └── kg_chat.py                            # LLM集成
├── docs/
│   └── knowledge_graph_guide.md                  # 使用指南
└── examples/
    └── knowledge_graph_example.py                # 示例代码
```

## 后续规划

- [ ] 支持Neo4j等专业图数据库
- [ ] Web可视化界面
- [ ] 自动从文档提取图谱
- [ ] 图谱推理引擎
- [ ] 多模态图谱支持

## 技术支持

- **详细文档**: `docs/knowledge_graph_guide.md`
- **示例代码**: `examples/knowledge_graph_example.py`
- **API文档**: http://localhost:7861/docs
- **问题反馈**: [GitHub Issues](https://github.com/chatchat-space/Langchain-Chatchat/issues)

## 版本信息

- **添加时间**: 2024-12
- **兼容版本**: Chatchat 0.3.x
- **Python版本**: >=3.8.1,<3.12
- **依赖**: networkx (已在原项目中)

## 贡献

欢迎提交Issue和PR来改进知识图谱功能！
