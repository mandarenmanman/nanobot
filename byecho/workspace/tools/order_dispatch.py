"""订单分发工具 — 将订单拆解为子任务并分发到各部门"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool


class OrderDispatchTool(Tool):
    """将订单拆解并分发到各部门。"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.orders_dir = workspace / "data" / "orders"
        self.orders_dir.mkdir(parents=True, exist_ok=True)

    @property
    def name(self) -> str:
        return "order_dispatch"

    @property
    def description(self) -> str:
        return (
            "创建订单并将任务分发到各部门。"
            "输入客户ID、柜型、数量、需求描述，输出订单ID和任务分配结果。"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "客户编号，如 C001",
                },
                "cabinet_type": {
                    "type": "string",
                    "description": "柜型名称，如 室内标准智能柜",
                },
                "quantity": {
                    "type": "integer",
                    "description": "订购数量",
                },
                "modules": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "功能模块列表，如 ['除湿模块','通信模块']",
                },
                "special_requirements": {
                    "type": "string",
                    "description": "特殊定制需求描述（可选）",
                },
            },
            "required": ["customer_id", "cabinet_type", "quantity"],
        }

    async def execute(
        self,
        customer_id: str,
        cabinet_type: str,
        quantity: int,
        modules: list[str] | None = None,
        special_requirements: str = "",
    ) -> str:
        now = datetime.now()
        order_id = f"ORD-{now.strftime('%Y')}-{now.strftime('%m%d%H%M%S')}"

        modules = modules or []
        is_custom = bool(special_requirements) or "非标" in cabinet_type

        # 根据模块需求决定哪些部门需要参与
        tasks = {}

        # 结构设计部 — 始终参与
        tasks["structural"] = {
            "status": "pending",
            "assignee": "结构设计部",
            "scope": "空间校验、图纸匹配",
            "priority": "high" if "户外" in cabinet_type else "normal",
        }

        # 硬件部 — 始终参与
        tasks["hardware"] = {
            "status": "pending",
            "assignee": "硬件部",
            "scope": "BOM审核、电路校验",
            "priority": "high",
        }

        # 软件部 — 有通信/IoT需求时参与
        if any(m in str(modules) for m in ["通信", "远程", "IoT", "监控"]):
            tasks["software"] = {
                "status": "pending",
                "assignee": "软件部",
                "scope": "IoT协议开发、控制程序",
                "priority": "normal",
            }

        # 行政部 — 需要打样或跨部门协调时参与
        if is_custom or quantity >= 100:
            tasks["admin"] = {
                "status": "pending",
                "assignee": "行政部",
                "scope": "打样资源排期" if is_custom else "批量生产协调",
                "priority": "normal",
            }

        # 供应链 — 始终参与
        tasks["supplier"] = {
            "status": "pending",
            "assignee": "供应链",
            "scope": "询价、备料、交期确认",
            "priority": "high",
        }

        order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "cabinet_type": cabinet_type,
            "quantity": quantity,
            "modules": modules,
            "special_requirements": special_requirements,
            "is_custom": is_custom,
            "status": "dispatched",
            "tasks": tasks,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        # 写入订单文件
        order_file = self.orders_dir / f"{order_id}.json"
        order_file.write_text(
            json.dumps(order, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # 生成分发摘要
        dept_list = ", ".join(t["assignee"] for t in tasks.values())
        summary = (
            f"订单 {order_id} 已创建并分发\n"
            f"- 客户: {customer_id}\n"
            f"- 柜型: {cabinet_type} × {quantity}台\n"
            f"- 类型: {'非标定制' if is_custom else '标准产品'}\n"
            f"- 参与部门: {dept_list}\n"
            f"- 订单文件: data/orders/{order_id}.json"
        )

        return summary
