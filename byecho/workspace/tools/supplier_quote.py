"""供应商询价工具 — 根据BOM自动匹配供应商并生成比价表"""

import json
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool


class SupplierQuoteTool(Tool):
    """根据BOM清单匹配供应商并生成比价表。"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.data_dir = workspace / "data"

    @property
    def name(self) -> str:
        return "supplier_quote"

    @property
    def description(self) -> str:
        return (
            "根据BOM清单匹配供应商，生成比价表。"
            "输入BOM模板文件名和订购数量，输出各元器件的供应商比价结果。"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "bom_file": {
                    "type": "string",
                    "description": "BOM模板文件名，如 standard_indoor.json",
                },
                "quantity": {
                    "type": "integer",
                    "description": "订购台数（用于计算总采购量）",
                    "minimum": 1,
                },
            },
            "required": ["bom_file", "quantity"],
        }

    async def execute(self, bom_file: str, quantity: int) -> str:
        bom_path = self.data_dir / "bom" / "templates" / bom_file
        if not bom_path.exists():
            return f"Error: BOM文件不存在: {bom_file}"

        supplier_path = self.data_dir / "suppliers" / "registry.json"
        bom = json.loads(bom_path.read_text(encoding="utf-8"))
        suppliers = {}
        if supplier_path.exists():
            reg = json.loads(supplier_path.read_text(encoding="utf-8"))
            suppliers = {s["code"]: s for s in reg.get("suppliers", [])}

        quotes = []
        total_cost = 0.0

        for module in bom.get("modules", []):
            for comp in module.get("components", []):
                total_qty = comp.get("quantity", 0) * quantity
                comp_quotes = []

                for sc in comp.get("supplier_codes", []):
                    if sc not in suppliers:
                        continue
                    s = suppliers[sc]

                    # 计算综合评分
                    m = s.get("metrics", {})
                    score = (
                        m.get("on_time_rate", 0) * 30
                        + (1 - m.get("defect_rate", 0)) * 30
                        + m.get("price_score", 0) * 20
                        + m.get("cooperation_score", 0) * 20
                    )

                    # 风险降权
                    risk_penalty = len(s.get("risk_flags", [])) * 5
                    score = max(0, score - risk_penalty)

                    unit_price = comp.get("unit_price", 0)
                    line_total = unit_price * total_qty

                    comp_quotes.append({
                        "supplier_code": sc,
                        "supplier_name": s["name"],
                        "level": s.get("level", "?"),
                        "unit_price": unit_price,
                        "total_qty": total_qty,
                        "line_total": round(line_total, 2),
                        "delivery_days": s.get("delivery_days", 0),
                        "score": round(score, 1),
                        "risk_flags": s.get("risk_flags", []),
                    })

                # 按评分排序，推荐最优
                comp_quotes.sort(key=lambda x: x["score"], reverse=True)
                recommended = comp_quotes[0] if comp_quotes else None
                if recommended:
                    total_cost += recommended["line_total"]

                quotes.append({
                    "component": comp["code"],
                    "name": comp["name"],
                    "module": module["module"],
                    "qty_per_unit": comp.get("quantity", 0),
                    "total_qty": total_qty,
                    "suppliers": comp_quotes,
                    "recommended": recommended["supplier_code"] if recommended else None,
                })

        result = {
            "bom_file": bom_file,
            "order_quantity": quantity,
            "quotes": quotes,
            "total_estimated_cost": round(total_cost, 2),
            "max_delivery_days": max(
                (q["suppliers"][0]["delivery_days"] for q in quotes if q["suppliers"]),
                default=0,
            ),
        }

        return json.dumps(result, ensure_ascii=False, indent=2)
