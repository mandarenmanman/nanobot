"""
将智能柜业务工具注册到 nanobot 的 AgentLoop 中。

使用方式：在 nanobot 启动后调用 register_byecho_tools(agent_loop)
或者在 config.json 中配置 MCP server 指向这些工具。

示例用法：
    from byecho.workspace.tools.register import register_byecho_tools
    register_byecho_tools(agent_loop, workspace_path)
"""

from pathlib import Path

from byecho.workspace.tools.analyst_inspect import AnalystInspectTool
from byecho.workspace.tools.bom_validate import BOMValidateTool
from byecho.workspace.tools.order_dispatch import OrderDispatchTool
from byecho.workspace.tools.supplier_quote import SupplierQuoteTool


def register_byecho_tools(agent_loop, workspace: Path | str | None = None):
    """将智能柜业务工具注册到 agent_loop 的 ToolRegistry 中。

    Args:
        agent_loop: nanobot 的 AgentLoop 实例
        workspace: 工作目录路径，默认使用 agent_loop.workspace
    """
    ws = Path(workspace) if workspace else agent_loop.workspace

    # 主轮工具
    agent_loop.tools.register(BOMValidateTool(ws))
    agent_loop.tools.register(OrderDispatchTool(ws))
    agent_loop.tools.register(SupplierQuoteTool(ws))

    # 辅轮工具（监事模型）
    agent_loop.tools.register(AnalystInspectTool(ws))

    return ["bom_validate", "order_dispatch", "supplier_quote", "analyst_inspect"]
