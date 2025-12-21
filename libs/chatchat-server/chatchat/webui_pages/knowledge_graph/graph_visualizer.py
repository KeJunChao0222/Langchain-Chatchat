"""
知识图谱可视化工具
提供多种可视化方式：Plotly交互式图谱、PyVis网络图、D3.js图谱
"""
import json
from typing import Dict, List
import streamlit as st
import streamlit.components.v1 as components


def visualize_with_plotly(nodes: List[Dict], edges: List[Dict]):
    """使用Plotly绘制交互式图谱"""
    try:
        import plotly.graph_objects as go
        import networkx as nx
        
        # 创建NetworkX图
        G = nx.DiGraph()
        
        # 添加节点
        node_colors = {}
        node_types = set()
        for node in nodes:
            node_id = node['node_id']
            node_type = node.get('node_type', '未分类')
            node_types.add(node_type)
            G.add_node(node_id, 
                      name=node['node_name'], 
                      type=node_type,
                      properties=node.get('properties', {}))
            node_colors[node_id] = node_type
        
        # 添加边
        for edge in edges:
            G.add_edge(edge['source_node_id'], 
                      edge['target_node_id'],
                      relation=edge.get('relation_type', '关联'),
                      weight=edge.get('weight', 1.0))
        
        # 使用spring layout布局
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # 为不同类型的节点分配颜色
        type_colors = {
            'Person': '#FF6B6B',
            'Company': '#4ECDC4',
            'Product': '#45B7D1',
            'Location': '#FFA07A',
            'Organization': '#98D8C8',
            'Event': '#FFD93D',
            '未分类': '#95A5A6'
        }
        
        # 创建边的轨迹
        edge_traces = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            # 计算箭头方向
            relation = edge[2].get('relation', '关联')
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=2, color='#888'),
                hoverinfo='text',
                text=f"{edge[0]} → [{relation}] → {edge[1]}",
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # 按类型分组节点
        node_traces_by_type = {}
        for node in G.nodes():
            node_type = G.nodes[node].get('type', '未分类')
            if node_type not in node_traces_by_type:
                node_traces_by_type[node_type] = {
                    'x': [],
                    'y': [],
                    'text': [],
                    'customdata': []
                }
            
            x, y = pos[node]
            node_traces_by_type[node_type]['x'].append(x)
            node_traces_by_type[node_type]['y'].append(y)
            node_traces_by_type[node_type]['text'].append(
                f"{G.nodes[node]['name']}<br>类型: {node_type}<br>ID: {node}"
            )
            node_traces_by_type[node_type]['customdata'].append(node)
        
        # 创建节点轨迹
        node_traces = []
        for node_type, data in node_traces_by_type.items():
            color = type_colors.get(node_type, '#95A5A6')
            
            node_trace = go.Scatter(
                x=data['x'],
                y=data['y'],
                mode='markers+text',
                marker=dict(
                    size=30,
                    color=color,
                    line=dict(width=2, color='white'),
                    symbol='circle'
                ),
                text=[G.nodes[n]['name'] for n in data['customdata']],
                textposition="top center",
                textfont=dict(size=10, color='black'),
                hoverinfo='text',
                hovertext=data['text'],
                name=node_type,
                customdata=data['customdata']
            )
            node_traces.append(node_trace)
        
        # 组合所有轨迹
        fig = go.Figure(data=edge_traces + node_traces)
        
        # 更新布局
        fig.update_layout(
            title={
                'text': '知识图谱可视化',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            showlegend=True,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(250,250,250,1)',
            height=700,
            legend=dict(
                title=dict(text='节点类型'),
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        # 显示图表
        st.plotly_chart(fig, use_container_width=True)
        return True
        
    except ImportError as e:
        st.error(f"❌ Plotly未安装: {e}")
        return False
    except Exception as e:
        st.error(f"❌ 可视化错误: {e}")
        return False


def visualize_with_pyvis(nodes: List[Dict], edges: List[Dict]):
    """使用PyVis生成交互式网络图"""
    try:
        from pyvis.network import Network
        import tempfile
        import os
        
        # 创建网络
        net = Network(
            height="700px",
            width="100%",
            bgcolor="#ffffff",
            font_color="black",
            directed=True
        )
        
        # 设置物理引擎
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 200,
              "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 150}
          }
        }
        """)
        
        # 定义颜色映射
        type_colors = {
            'Person': '#FF6B6B',
            'Company': '#4ECDC4',
            'Product': '#45B7D1',
            'Location': '#FFA07A',
            'Organization': '#98D8C8',
            'Event': '#FFD93D',
            '未分类': '#95A5A6'
        }
        
        # 添加节点
        for node in nodes:
            node_id = node['node_id']
            node_name = node['node_name']
            node_type = node.get('node_type', '未分类')
            color = type_colors.get(node_type, '#95A5A6')
            
            # 构建标题（悬停显示）
            title = f"<b>{node_name}</b><br>"
            title += f"ID: {node_id}<br>"
            title += f"类型: {node_type}"
            
            if node.get('properties'):
                try:
                    props = json.loads(node['properties']) if isinstance(node['properties'], str) else node['properties']
                    title += "<br><br><b>属性:</b><br>"
                    for k, v in props.items():
                        title += f"{k}: {v}<br>"
                except:
                    pass
            
            net.add_node(
                node_id,
                label=node_name,
                title=title,
                color=color,
                size=25,
                font={'size': 14}
            )
        
        # 添加边
        for edge in edges:
            source = edge['source_node_id']
            target = edge['target_node_id']
            relation = edge.get('relation_type', '关联')
            weight = edge.get('weight', 1.0)
            
            net.add_edge(
                source,
                target,
                title=relation,
                label=relation,
                arrows='to',
                color={'color': '#888888'},
                width=weight * 2,
                font={'size': 10, 'align': 'middle'}
            )
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
            html_file = f.name
            net.save_graph(html_file)
        
        # 读取并显示
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 清理临时文件
        os.unlink(html_file)
        
        # 显示在streamlit中
        components.html(html_content, height=750, scrolling=False)
        return True
        
    except ImportError as e:
        st.error(f"❌ PyVis未安装: {e}")
        st.info("💡 安装命令: `pip install pyvis`")
        return False
    except Exception as e:
        st.error(f"❌ 可视化错误: {e}")
        return False


def visualize_with_d3js(nodes: List[Dict], edges: List[Dict]):
    """使用D3.js绘制力导向图（原生JavaScript，无需额外依赖）"""
    
    # 准备数据
    d3_nodes = []
    for node in nodes:
        d3_nodes.append({
            'id': node['node_id'],
            'name': node['node_name'],
            'type': node.get('node_type', '未分类'),
            'properties': node.get('properties', {})
        })
    
    d3_edges = []
    for edge in edges:
        d3_edges.append({
            'source': edge['source_node_id'],
            'target': edge['target_node_id'],
            'relation': edge.get('relation_type', '关联'),
            'weight': edge.get('weight', 1.0)
        })
    
    # 构建HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }}
            #graph {{
                width: 100%;
                height: 700px;
                border: 1px solid #ddd;
                background-color: #fafafa;
            }}
            .node {{
                cursor: pointer;
                stroke: #fff;
                stroke-width: 2px;
            }}
            .node text {{
                font-size: 12px;
                pointer-events: none;
            }}
            .link {{
                stroke: #999;
                stroke-opacity: 0.6;
            }}
            .link-label {{
                font-size: 10px;
                fill: #666;
            }}
            .tooltip {{
                position: absolute;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
                pointer-events: none;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                z-index: 1000;
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script>
            const nodes = {json.dumps(d3_nodes)};
            const links = {json.dumps(d3_edges)};
            
            // 颜色映射
            const typeColors = {{
                'Person': '#FF6B6B',
                'Company': '#4ECDC4',
                'Product': '#45B7D1',
                'Location': '#FFA07A',
                'Organization': '#98D8C8',
                'Event': '#FFD93D',
                '未分类': '#95A5A6'
            }};
            
            const width = document.getElementById('graph').clientWidth;
            const height = 700;
            
            // 创建SVG
            const svg = d3.select("#graph")
                .append("svg")
                .attr("width", width)
                .attr("height", height);
            
            // 创建tooltip
            const tooltip = d3.select("body")
                .append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);
            
            // 创建力导向模拟
            const simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id).distance(150))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(40));
            
            // 添加箭头标记
            svg.append("defs").selectAll("marker")
                .data(["arrow"])
                .enter().append("marker")
                .attr("id", d => d)
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 25)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#999");
            
            // 绘制连线
            const link = svg.append("g")
                .selectAll("line")
                .data(links)
                .enter().append("line")
                .attr("class", "link")
                .attr("marker-end", "url(#arrow)")
                .style("stroke-width", d => Math.sqrt(d.weight) * 2);
            
            // 连线标签
            const linkLabel = svg.append("g")
                .selectAll("text")
                .data(links)
                .enter().append("text")
                .attr("class", "link-label")
                .text(d => d.relation);
            
            // 绘制节点
            const node = svg.append("g")
                .selectAll("g")
                .data(nodes)
                .enter().append("g")
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            // 节点圆圈
            node.append("circle")
                .attr("class", "node")
                .attr("r", 20)
                .style("fill", d => typeColors[d.type] || typeColors['未分类'])
                .on("mouseover", function(event, d) {{
                    d3.select(this).transition()
                        .duration(200)
                        .attr("r", 25);
                    
                    let html = `<b>${{d.name}}</b><br>`;
                    html += `ID: ${{d.id}}<br>`;
                    html += `类型: ${{d.type}}`;
                    
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    tooltip.html(html)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                }})
                .on("mouseout", function(d) {{
                    d3.select(this).transition()
                        .duration(200)
                        .attr("r", 20);
                    
                    tooltip.transition()
                        .duration(500)
                        .style("opacity", 0);
                }});
            
            // 节点标签
            node.append("text")
                .text(d => d.name)
                .attr("x", 0)
                .attr("y", -25)
                .attr("text-anchor", "middle")
                .style("font-weight", "bold");
            
            // 更新位置
            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                linkLabel
                    .attr("x", d => (d.source.x + d.target.x) / 2)
                    .attr("y", d => (d.source.y + d.target.y) / 2);
                
                node
                    .attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            }});
            
            // 拖拽函数
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}
            
            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}
            
            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
        </script>
    </body>
    </html>
    """
    
    # 显示
    components.html(html_content, height=750, scrolling=False)
    return True


def show_graph_visualization(nodes: List[Dict], edges: List[Dict], method: str = "d3js"):
    """
    显示图谱可视化
    
    Args:
        nodes: 节点列表
        edges: 边列表
        method: 可视化方法 ('plotly', 'pyvis', 'd3js')
    """
    if not nodes:
        st.warning("⚠️ 暂无节点数据，无法可视化")
        return False
    
    if method == "plotly":
        return visualize_with_plotly(nodes, edges)
    elif method == "pyvis":
        return visualize_with_pyvis(nodes, edges)
    elif method == "d3js":
        return visualize_with_d3js(nodes, edges)
    else:
        st.error(f"❌ 不支持的可视化方法: {method}")
        return False
