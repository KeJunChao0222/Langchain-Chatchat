"""
知识图谱管理页面
提供图谱的可视化、节点/边管理、导入导出等功能
"""
import json
from typing import Dict, List

import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from chatchat.webui_pages.utils import *
from chatchat.webui_pages.knowledge_graph.graph_visualizer import show_graph_visualization


def knowledge_graph_page(api: ApiRequest, is_lite: bool = False):
    """知识图谱管理主页面"""

    st.title("📊 知识图谱管理")
    st.caption("构建和管理结构化知识，支持实体关系抽取和图谱推理")

    # 初始化session state
    if "kg_kb_name" not in st.session_state:
        st.session_state.kg_kb_name = ""
    if "kg_selected_tab" not in st.session_state:
        st.session_state.kg_selected_tab = "图谱概览"

    # 顶部工具栏
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            # 知识库选择
            kb_list = api.list_knowledge_bases()
            kb_names = [kb["kb_name"] for kb in kb_list] if kb_list else []

            if kb_names:
                st.session_state.kg_kb_name = st.selectbox(
                    "选择知识库",
                    kb_names,
                    index=0 if not st.session_state.kg_kb_name else (
                        kb_names.index(st.session_state.kg_kb_name)
                        if st.session_state.kg_kb_name in kb_names
                        else 0
                    ),
                    key="kg_kb_selector",
                )
            else:
                st.warning("⚠️ 暂无知识库，请先创建知识库")
                return

        with col2:
            # 获取图谱统计
            if st.button("🔄 刷新统计", use_container_width=True):
                st.rerun()

        with col3:
            # 清空图谱
            if st.button("🗑️ 清空图谱", type="secondary", use_container_width=True):
                if st.session_state.kg_kb_name:
                    with st.spinner("清空中..."):
                        result = api.clear_knowledge_graph(st.session_state.kg_kb_name)
                        if result.get("code") == 200:
                            st.success("✅ 图谱已清空")
                            st.rerun()
                        else:
                            st.error(f"❌ 清空失败: {result.get('msg')}")

    st.divider()

    # 标签页导航
    selected_tab = sac.tabs(
        [
            sac.TabsItem(label="图谱概览", icon="bar-chart"),
            sac.TabsItem(label="节点管理", icon="circle"),
            sac.TabsItem(label="关系管理", icon="arrow-left-right"),
            sac.TabsItem(label="图谱可视化", icon="diagram-3"),
            sac.TabsItem(label="图谱对话", icon="chat-dots"),
            sac.TabsItem(label="导入导出", icon="arrow-down-up"),
        ],
        align="center",
        return_index=False,
        key="kg_tabs",
    )

    kb_name = st.session_state.kg_kb_name

    # 根据选择的标签显示不同内容
    if selected_tab == "图谱概览":
        show_graph_overview(api, kb_name)
    elif selected_tab == "节点管理":
        show_node_management(api, kb_name)
    elif selected_tab == "关系管理":
        show_edge_management(api, kb_name)
    elif selected_tab == "图谱可视化":
        show_graph_visualization(api, kb_name)
    elif selected_tab == "图谱对话":
        show_graph_chat(api, kb_name)
    elif selected_tab == "导入导出":
        show_import_export(api, kb_name)


def show_graph_overview(api: ApiRequest, kb_name: str):
    """显示图谱概览"""
    st.header("📈 图谱概览")

    # 获取统计信息
    stats_result = api.get_graph_stats(kb_name)

    if stats_result.get("code") == 200:
        stats = stats_result.get("data", {})

        # 显示统计卡片
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="📍 节点数量",
                value=stats.get("node_count", 0),
                help="图谱中的实体总数",
            )

        with col2:
            st.metric(
                label="🔗 关系数量",
                value=stats.get("edge_count", 0),
                help="图谱中的关系总数",
            )

        with col3:
            density = 0
            if stats.get("node_count", 0) > 1:
                max_edges = stats.get("node_count", 0) * (stats.get("node_count", 0) - 1)
                density = (
                    stats.get("edge_count", 0) / max_edges * 100
                    if max_edges > 0
                    else 0
                )
            st.metric(
                label="📊 图谱密度",
                value=f"{density:.2f}%",
                help="实际关系数占可能最大关系数的比例",
            )

        st.divider()

        # 最近的节点
        st.subheader("🔍 最近的节点")
        nodes_result = api.list_graph_nodes(kb_name, limit=10)
        if nodes_result.get("code") == 200:
            nodes = nodes_result.get("data", [])
            if nodes:
                df = pd.DataFrame(nodes)
                df = df[["node_id", "node_name", "node_type", "create_time"]]
                df.columns = ["节点ID", "节点名称", "节点类型", "创建时间"]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("暂无节点数据")

        st.divider()

        # 最近的关系
        st.subheader("🔗 最近的关系")
        edges_result = api.list_graph_edges(kb_name, limit=10)
        if edges_result.get("code") == 200:
            edges = edges_result.get("data", [])
            if edges:
                df = pd.DataFrame(edges)
                df = df[
                    [
                        "source_node_id",
                        "relation_type",
                        "target_node_id",
                        "weight",
                        "create_time",
                    ]
                ]
                df.columns = ["源节点", "关系类型", "目标节点", "权重", "创建时间"]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("暂无关系数据")
    else:
        st.error(f"获取统计信息失败: {stats_result.get('msg')}")


def show_node_management(api: ApiRequest, kb_name: str):
    """节点管理界面"""
    st.header("🔵 节点管理")

    # 操作选择
    operation = sac.segmented(
        items=[
            sac.SegmentedItem(label="查看节点", icon="list"),
            sac.SegmentedItem(label="创建节点", icon="plus-circle"),
            sac.SegmentedItem(label="批量创建", icon="file-earmark-plus"),
        ],
        align="center",
        return_index=False,
        key="node_operation",
    )

    if operation == "查看节点":
        show_node_list(api, kb_name)
    elif operation == "创建节点":
        show_create_node(api, kb_name)
    elif operation == "批量创建":
        show_batch_create_nodes(api, kb_name)


def show_node_list(api: ApiRequest, kb_name: str):
    """显示节点列表"""
    st.subheader("节点列表")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        search_keyword = st.text_input("🔍 搜索节点", placeholder="输入节点名称或类型")

    with col2:
        node_type_filter = st.text_input("🏷️ 节点类型过滤", placeholder="如: Person, Company")

    with col3:
        limit = st.number_input("显示数量", min_value=10, max_value=1000, value=50)

    # 搜索或列出节点
    if search_keyword:
        nodes_result = api.search_graph_nodes(kb_name, search_keyword, limit)
    else:
        nodes_result = api.list_graph_nodes(kb_name, node_type_filter, limit)

    if nodes_result.get("code") == 200:
        nodes = nodes_result.get("data", [])

        if nodes:
            st.success(f"找到 {len(nodes)} 个节点")

            # 显示节点表格
            for i, node in enumerate(nodes):
                with st.expander(
                    f"📍 {node['node_name']} ({node.get('node_type', 'N/A')})"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**节点ID:** {node['node_id']}")
                        st.write(f"**节点类型:** {node.get('node_type', 'N/A')}")
                        st.write(f"**创建时间:** {node.get('create_time', 'N/A')}")

                    with col2:
                        if node.get("properties"):
                            try:
                                props = (
                                    json.loads(node["properties"])
                                    if isinstance(node["properties"], str)
                                    else node["properties"]
                                )
                                st.write("**属性:**")
                                st.json(props)
                            except:
                                st.write(f"**属性:** {node['properties']}")

                    # 操作按钮
                    col_a, col_b, col_c = st.columns(3)

                    with col_a:
                        if st.button(
                            "🔍 查看邻居", key=f"neighbors_{i}", use_container_width=True
                        ):
                            st.session_state[f"show_neighbors_{i}"] = True

                    with col_b:
                        if st.button(
                            "✏️ 编辑", key=f"edit_{i}", use_container_width=True
                        ):
                            st.session_state[f"edit_node_{i}"] = node

                    with col_c:
                        if st.button(
                            "🗑️ 删除",
                            key=f"delete_{i}",
                            type="secondary",
                            use_container_width=True,
                        ):
                            result = api.delete_graph_node(kb_name, node["node_id"])
                            if result.get("code") == 200:
                                st.success("✅ 节点已删除")
                                st.rerun()
                            else:
                                st.error(f"❌ 删除失败: {result.get('msg')}")

                    # 显示邻居
                    if st.session_state.get(f"show_neighbors_{i}"):
                        neighbors_result = api.get_node_neighbors(
                            kb_name, node["node_id"], "both", 1
                        )
                        if neighbors_result.get("code") == 200:
                            data = neighbors_result.get("data", {})
                            st.write(f"**邻居节点数:** {len(data.get('nodes', []))}")
                            st.write(f"**相关关系数:** {len(data.get('edges', []))}")
        else:
            st.info("暂无节点数据")
    else:
        st.error(f"查询失败: {nodes_result.get('msg')}")


def show_create_node(api: ApiRequest, kb_name: str):
    """创建单个节点"""
    st.subheader("创建新节点")

    with st.form("create_node_form"):
        node_id = st.text_input(
            "节点ID *",
            help="节点的唯一标识符",
            placeholder="如: person_001, company_abc",
        )

        node_name = st.text_input(
            "节点名称 *", help="节点的显示名称", placeholder="如: 张三, 阿里巴巴"
        )

        node_type = st.text_input(
            "节点类型", help="节点的类型分类", placeholder="如: Person, Company, Product"
        )

        properties_text = st.text_area(
            "节点属性 (JSON格式)",
            help='节点的自定义属性，JSON格式，如: {"age": 30, "city": "北京"}',
            placeholder='{"age": 30, "city": "北京"}',
        )

        submitted = st.form_submit_button("创建节点", type="primary", use_container_width=True)

        if submitted:
            if not node_id or not node_name:
                st.error("❌ 节点ID和节点名称为必填项")
            else:
                # 解析属性
                properties = None
                if properties_text.strip():
                    try:
                        properties = json.loads(properties_text)
                    except json.JSONDecodeError:
                        st.error("❌ 属性格式错误，请输入有效的JSON")
                        return

                # 调用API创建节点
                result = api.create_graph_node(
                    kb_name=kb_name,
                    node_id=node_id,
                    node_name=node_name,
                    node_type=node_type,
                    properties=properties,
                )

                if result.get("code") == 200:
                    st.success(f"✅ 节点 '{node_name}' 创建成功！")
                    st.balloons()
                else:
                    st.error(f"❌ 创建失败: {result.get('msg')}")


def show_batch_create_nodes(api: ApiRequest, kb_name: str):
    """批量创建节点"""
    st.subheader("批量创建节点")

    st.info(
        """
    **批量创建说明:**
    - 每行一个节点
    - 格式: `节点ID,节点名称,节点类型`
    - 节点类型可选
    - 示例: `person_001,张三,Person`
    """
    )

    nodes_text = st.text_area(
        "输入节点数据（每行一个）",
        height=200,
        placeholder="person_001,张三,Person\nperson_002,李四,Person\ncompany_001,阿里巴巴,Company",
    )

    if st.button("批量创建", type="primary", use_container_width=True):
        if not nodes_text.strip():
            st.error("❌ 请输入节点数据")
            return

        lines = [line.strip() for line in nodes_text.split("\n") if line.strip()]
        nodes = []

        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                node = {
                    "node_id": parts[0],
                    "node_name": parts[1],
                    "node_type": parts[2] if len(parts) > 2 else None,
                }
                nodes.append(node)

        if nodes:
            with st.spinner(f"正在创建 {len(nodes)} 个节点..."):
                result = api.batch_create_graph_nodes(kb_name, nodes)

                if result.get("code") == 200:
                    st.success(f"✅ {result.get('msg')}")
                    st.balloons()
                else:
                    st.error(f"❌ 批量创建失败: {result.get('msg')}")
        else:
            st.error("❌ 没有有效的节点数据")


def show_edge_management(api: ApiRequest, kb_name: str):
    """关系管理界面"""
    st.header("🔗 关系管理")

    operation = sac.segmented(
        items=[
            sac.SegmentedItem(label="查看关系", icon="list"),
            sac.SegmentedItem(label="创建关系", icon="plus-circle"),
            sac.SegmentedItem(label="批量创建", icon="file-earmark-plus"),
        ],
        align="center",
        return_index=False,
        key="edge_operation",
    )

    if operation == "查看关系":
        show_edge_list(api, kb_name)
    elif operation == "创建关系":
        show_create_edge(api, kb_name)
    elif operation == "批量创建":
        show_batch_create_edges(api, kb_name)


def show_edge_list(api: ApiRequest, kb_name: str):
    """显示关系列表"""
    st.subheader("关系列表")

    col1, col2, col3 = st.columns(3)

    with col1:
        node_id_filter = st.text_input("🔍 按节点ID筛选", placeholder="输入节点ID")

    with col2:
        relation_type_filter = st.text_input(
            "🏷️ 关系类型过滤", placeholder="如: knows, works_at"
        )

    with col3:
        limit = st.number_input("显示数量", min_value=10, max_value=1000, value=50)

    edges_result = api.list_graph_edges(kb_name, node_id_filter, relation_type_filter, limit)

    if edges_result.get("code") == 200:
        edges = edges_result.get("data", [])

        if edges:
            st.success(f"找到 {len(edges)} 条关系")

            # 显示关系表格
            for i, edge in enumerate(edges):
                with st.expander(
                    f"🔗 {edge['source_node_id']} → [{edge.get('relation_type', 'N/A')}] → {edge['target_node_id']}"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**边ID:** {edge['edge_id']}")
                        st.write(f"**源节点:** {edge['source_node_id']}")
                        st.write(f"**目标节点:** {edge['target_node_id']}")

                    with col2:
                        st.write(f"**关系类型:** {edge.get('relation_type', 'N/A')}")
                        st.write(f"**权重:** {edge.get('weight', 1.0)}")
                        st.write(f"**创建时间:** {edge.get('create_time', 'N/A')}")

                    if edge.get("properties"):
                        try:
                            props = (
                                json.loads(edge["properties"])
                                if isinstance(edge["properties"], str)
                                else edge["properties"]
                            )
                            st.write("**属性:**")
                            st.json(props)
                        except:
                            pass

                    # 删除按钮
                    if st.button(
                        "🗑️ 删除",
                        key=f"delete_edge_{i}",
                        type="secondary",
                        use_container_width=True,
                    ):
                        result = api.delete_graph_edge(kb_name, edge["edge_id"])
                        if result.get("code") == 200:
                            st.success("✅ 关系已删除")
                            st.rerun()
                        else:
                            st.error(f"❌ 删除失败: {result.get('msg')}")
        else:
            st.info("暂无关系数据")
    else:
        st.error(f"查询失败: {edges_result.get('msg')}")


def show_create_edge(api: ApiRequest, kb_name: str):
    """创建单条关系"""
    st.subheader("创建新关系")

    with st.form("create_edge_form"):
        source_node_id = st.text_input(
            "源节点ID *", help="关系的起始节点", placeholder="如: person_001"
        )

        relation_type = st.text_input(
            "关系类型", help="关系的类型", placeholder="如: knows, works_at, friend_of"
        )

        target_node_id = st.text_input(
            "目标节点ID *", help="关系的目标节点", placeholder="如: person_002"
        )

        weight = st.number_input(
            "权重", min_value=0.0, max_value=10.0, value=1.0, step=0.1, help="关系的权重"
        )

        properties_text = st.text_area(
            "关系属性 (JSON格式)",
            help='关系的自定义属性，如: {"since": "2020", "type": "colleague"}',
            placeholder='{"since": "2020"}',
        )

        submitted = st.form_submit_button("创建关系", type="primary", use_container_width=True)

        if submitted:
            if not source_node_id or not target_node_id:
                st.error("❌ 源节点ID和目标节点ID为必填项")
            else:
                # 解析属性
                properties = None
                if properties_text.strip():
                    try:
                        properties = json.loads(properties_text)
                    except json.JSONDecodeError:
                        st.error("❌ 属性格式错误，请输入有效的JSON")
                        return

                # 调用API创建关系
                result = api.create_graph_edge(
                    kb_name=kb_name,
                    source_node_id=source_node_id,
                    target_node_id=target_node_id,
                    relation_type=relation_type,
                    properties=properties,
                    weight=weight,
                )

                if result.get("code") == 200:
                    st.success(f"✅ 关系创建成功！")
                    st.balloons()
                else:
                    st.error(f"❌ 创建失败: {result.get('msg')}")


def show_batch_create_edges(api: ApiRequest, kb_name: str):
    """批量创建关系"""
    st.subheader("批量创建关系")

    st.info(
        """
    **批量创建说明:**
    - 每行一条关系
    - 格式: `源节点ID,关系类型,目标节点ID`
    - 示例: `person_001,knows,person_002`
    """
    )

    edges_text = st.text_area(
        "输入关系数据（每行一条）",
        height=200,
        placeholder="person_001,knows,person_002\nperson_001,works_at,company_001\nperson_002,friend_of,person_003",
    )

    if st.button("批量创建", type="primary", use_container_width=True):
        if not edges_text.strip():
            st.error("❌ 请输入关系数据")
            return

        lines = [line.strip() for line in edges_text.split("\n") if line.strip()]
        edges = []

        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                edge = {
                    "source_node_id": parts[0],
                    "relation_type": parts[1],
                    "target_node_id": parts[2],
                }
                edges.append(edge)

        if edges:
            with st.spinner(f"正在创建 {len(edges)} 条关系..."):
                result = api.batch_create_graph_edges(kb_name, edges)

                if result.get("code") == 200:
                    st.success(f"✅ {result.get('msg')}")
                    st.balloons()
                else:
                    st.error(f"❌ 批量创建失败: {result.get('msg')}")
        else:
            st.error("❌ 没有有效的关系数据")


def show_graph_visualization(api: ApiRequest, kb_name: str):
    """图谱可视化"""
    st.header("🎨 图谱可视化")

    st.caption("交互式3D图谱，支持拖拽节点、缩放、悬停查看详情")

    # 可视化选项
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        viz_method = st.selectbox(
            "选择可视化方式",
            ["D3.js 力导向图 (推荐)", "Plotly 交互图", "PyVis 网络图"],
            help="D3.js: 原生JavaScript，无需额外依赖\nPlotly: 需要plotly库\nPyVis: 需要pyvis库"
        )

    with col2:
        max_nodes = st.number_input("最大节点数", min_value=10, max_value=500, value=100)

    with col3:
        refresh_btn = st.button("🔄 刷新", use_container_width=True)

    # 映射可视化方法
    method_map = {
        "D3.js 力导向图 (推荐)": "d3js",
        "Plotly 交互图": "plotly",
        "PyVis 网络图": "pyvis"
    }
    selected_method = method_map[viz_method]

    # 加载和显示图谱
    if st.button("🎨 生成可视化", type="primary", use_container_width=True) or refresh_btn:
        with st.spinner("加载图谱数据..."):
            # 获取节点和边
            nodes_result = api.list_graph_nodes(kb_name, limit=max_nodes)
            edges_result = api.list_graph_edges(kb_name, limit=max_nodes * 2)

            if nodes_result.get("code") == 200 and edges_result.get("code") == 200:
                nodes = nodes_result.get("data", [])
                edges = edges_result.get("data", [])

                if nodes:
                    st.success(f"✅ 加载了 {len(nodes)} 个节点和 {len(edges)} 条边")

                    # 显示图例
                    with st.expander("📖 图例说明", expanded=False):
                        st.markdown("""
                        **节点颜色：**
                        - � Person (人物) - 红色
                        - 🟢 Company (公司) - 青色  
                        - 🔵 Product (产品) - 蓝色
                        - 🟠 Location (地点) - 橙色
                        - 🟣 Organization (组织) - 绿色
                        - 🟡 Event (事件) - 黄色
                        - ⚫ 未分类 - 灰色
                        
                        **操作提示：**
                        - 🖱️ 拖拽节点可以移动位置
                        - � 鼠标悬停查看节点详情
                        - ↔️ 箭头表示关系方向
                        - � 线条粗细表示关系权重
                        """)

                    st.divider()

                    # 显示可视化
                    from chatchat.webui_pages.knowledge_graph.graph_visualizer import show_graph_visualization as viz
                    success = viz(nodes, edges, method=selected_method)

                    if success:
                        st.divider()

                        # 显示统计信息
                        with st.expander("📊 图谱统计", expanded=True):
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                # 节点类型统计
                                node_types = {}
                                for node in nodes:
                                    ntype = node.get("node_type") or "未分类"
                                    node_types[ntype] = node_types.get(ntype, 0) + 1
                                
                                st.write("**节点类型分布:**")
                                for ntype, count in sorted(node_types.items(), key=lambda x: -x[1]):
                                    st.write(f"- {ntype}: {count}")
                            
                            with col_b:
                                # 关系类型统计
                                if edges:
                                    relation_types = {}
                                    for edge in edges:
                                        rtype = edge.get("relation_type") or "未分类"
                                        relation_types[rtype] = relation_types.get(rtype, 0) + 1
                                    
                                    st.write("**关系类型分布:**")
                                    for rtype, count in sorted(relation_types.items(), key=lambda x: -x[1]):
                                        st.write(f"- {rtype}: {count}")
                            
                            with col_c:
                                st.write("**图谱度量:**")
                                st.write(f"- 总节点数: {len(nodes)}")
                                st.write(f"- 总边数: {len(edges)}")
                                if len(nodes) > 1:
                                    max_edges = len(nodes) * (len(nodes) - 1)
                                    density = len(edges) / max_edges * 100 if max_edges > 0 else 0
                                    st.write(f"- 密度: {density:.2f}%")

                else:
                    st.info("📭 图谱为空，请先添加节点和关系")
                    st.markdown("""
                    **快速开始：**
                    1. 进入 **"节点管理"** 标签创建节点
                    2. 进入 **"关系管理"** 标签创建关系
                    3. 返回此处查看可视化效果
                    """)
            else:
                st.error("❌ 加载图谱数据失败")

    # 提供示例数据生成
    st.divider()
    with st.expander("🎲 生成示例图谱", expanded=False):
        st.info("快速生成一个示例图谱用于测试可视化效果")
        
        if st.button("生成公司组织架构示例", use_container_width=True):
            example_nodes = [
                {"node_id": "ceo", "node_name": "CEO张三", "node_type": "Person"},
                {"node_id": "cto", "node_name": "CTO李四", "node_type": "Person"},
                {"node_id": "cfo", "node_name": "CFO王五", "node_type": "Person"},
                {"node_id": "tech_dept", "node_name": "技术部", "node_type": "Organization"},
                {"node_id": "finance_dept", "node_name": "财务部", "node_type": "Organization"},
                {"node_id": "company", "node_name": "ABC科技公司", "node_type": "Company"},
            ]
            
            example_edges = [
                {"source_node_id": "ceo", "relation_type": "管理", "target_node_id": "company"},
                {"source_node_id": "cto", "relation_type": "负责", "target_node_id": "tech_dept"},
                {"source_node_id": "cfo", "relation_type": "负责", "target_node_id": "finance_dept"},
                {"source_node_id": "ceo", "relation_type": "领导", "target_node_id": "cto"},
                {"source_node_id": "ceo", "relation_type": "领导", "target_node_id": "cfo"},
                {"source_node_id": "tech_dept", "relation_type": "属于", "target_node_id": "company"},
                {"source_node_id": "finance_dept", "relation_type": "属于", "target_node_id": "company"},
            ]
            
            with st.spinner("创建示例图谱..."):
                # 批量创建
                nodes_result = api.batch_create_graph_nodes(kb_name, example_nodes)
                edges_result = api.batch_create_graph_edges(kb_name, example_edges)
                
                if nodes_result.get("code") == 200 and edges_result.get("code") == 200:
                    st.success("✅ 示例图谱创建成功！点击上方'生成可视化'按钮查看效果")
                    st.balloons()
                else:
                    st.error("❌ 创建失败")


def show_graph_chat(api: ApiRequest, kb_name: str):
    """图谱对话"""
    st.header("💬 知识图谱对话")

    st.info("基于知识图谱的智能问答，LLM会自动从图谱中提取相关信息作为上下文")

    # 初始化对话历史
    if "kg_chat_history" not in st.session_state:
        st.session_state.kg_chat_history = []

    # 显示对话历史
    for msg in st.session_state.kg_chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 输入框
    user_input = st.chat_input("输入你的问题...")

    if user_input:
        # 添加用户消息
        st.session_state.kg_chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        # 调用API
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                # 简单查询（不使用LLM）
                result = api.simple_graph_query(kb_name, user_input, top_k=10)

                if result.get("code") == 200:
                    data = result.get("data", {})
                    nodes = data.get("nodes", [])
                    edges = data.get("edges", [])

                    if nodes or edges:
                        response = f"找到 {len(nodes)} 个相关节点和 {len(edges)} 条相关关系:\n\n"

                        if nodes:
                            response += "**相关实体:**\n"
                            for node in nodes[:5]:
                                response += f"- {node['node_name']} ({node.get('node_type', 'N/A')})\n"

                        if edges:
                            response += "\n**相关关系:**\n"
                            for edge in edges[:5]:
                                response += f"- {edge['source_node_id']} → [{edge.get('relation_type', 'N/A')}] → {edge['target_node_id']}\n"

                        st.write(response)
                        st.session_state.kg_chat_history.append(
                            {"role": "assistant", "content": response}
                        )

                        # 显示详细数据
                        with st.expander("查看详细数据"):
                            st.json(data)
                    else:
                        response = "未找到相关的图谱信息"
                        st.write(response)
                        st.session_state.kg_chat_history.append(
                            {"role": "assistant", "content": response}
                        )
                else:
                    st.error(f"查询失败: {result.get('msg')}")

    # 清空对话
    if st.button("🗑️ 清空对话历史"):
        st.session_state.kg_chat_history = []
        st.rerun()


def show_import_export(api: ApiRequest, kb_name: str):
    """导入导出"""
    st.header("💾 图谱导入导出")

    tab1, tab2 = st.tabs(["📤 导出图谱", "📥 导入图谱"])

    with tab1:
        st.subheader("导出图谱数据")

        st.write("将当前图谱导出为JSON格式，可用于备份或迁移")

        if st.button("导出图谱", type="primary", use_container_width=True):
            with st.spinner("导出中..."):
                result = api.export_knowledge_graph(kb_name)

                if result.get("code") == 200:
                    graph_data = result.get("data", {})

                    # 转换为JSON字符串
                    json_str = json.dumps(graph_data, ensure_ascii=False, indent=2)

                    st.success(
                        f"✅ 导出成功！节点: {len(graph_data.get('nodes', []))}, 边: {len(graph_data.get('edges', []))}"
                    )

                    # 下载按钮
                    st.download_button(
                        label="💾 下载JSON文件",
                        data=json_str,
                        file_name=f"{kb_name}_graph_export.json",
                        mime="application/json",
                        use_container_width=True,
                    )

                    # 预览
                    with st.expander("预览数据"):
                        st.json(graph_data)
                else:
                    st.error(f"❌ 导出失败: {result.get('msg')}")

    with tab2:
        st.subheader("导入图谱数据")

        st.write("从JSON文件导入图谱数据")

        uploaded_file = st.file_uploader("选择JSON文件", type=["json"])

        clear_existing = st.checkbox("导入前清空现有图谱", value=False)

        if uploaded_file is not None:
            try:
                # 读取文件
                graph_data = json.load(uploaded_file)

                # 预览
                st.write("**文件预览:**")
                st.write(f"- 节点数: {len(graph_data.get('nodes', []))}")
                st.write(f"- 边数: {len(graph_data.get('edges', []))}")

                with st.expander("查看详细内容"):
                    st.json(graph_data)

                if st.button("开始导入", type="primary", use_container_width=True):
                    with st.spinner("导入中..."):
                        result = api.import_knowledge_graph(
                            kb_name, graph_data, clear_existing
                        )

                        if result.get("code") == 200:
                            st.success(f"✅ {result.get('msg')}")
                            st.balloons()
                        else:
                            st.error(f"❌ 导入失败: {result.get('msg')}")

            except json.JSONDecodeError:
                st.error("❌ 文件格式错误，请上传有效的JSON文件")
            except Exception as e:
                st.error(f"❌ 读取文件失败: {str(e)}")
