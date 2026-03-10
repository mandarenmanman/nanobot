"""BOM校验工具 — 检查停产元器件、负载计算、供应商可用性"""

import json
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool


class BOMValidateTool(Tool):
    """校验BOM清单的完整性和风险。"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.data_dir = workspace / "data"

    @property
    def name(self) -> str:
        return "bom_validate"

    @property
    def description(self) -> str:
        return (
            "校验BOM清单：检查停产元器件、电路负载计算、供应商可用性。"
            "输入BOM模板文件名，输出校验报告。"
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
            },
            "required": ["bom_file"],
        }

    async def execute(self, bom_file: str) -> str:
        bom_path = self.data_dir / "bom" / "templates" / bom_file
        if not bom_path.exists():
            return f"Error: BOM文件不存在: {bom_file}"

        supplier_path = self.data_dir / "suppliers" / "registry.json"
        rules_path = self.data_dir / "rules" / "structural_rules.json"

        bom = json.loads(bom_path.read_text(encoding="utf-8"))
        suppliers = {}
        if supplier_path.exists():
            reg = json.loads(supplier_path.read_text(encoding="utf-8"))
            suppliers = {s["code"]: s for s in reg.get("suppliers", [])}

        rules = []
        if rules_path.exists():
            rules_data = json.loads(rules_path.read_text(encoding="utf-8"))
            rules = rules_data.get("rules", [])

        report = {
            "bom_file": bom_file,
            "cabinet_type": bom.get("cabinet_type", "未知"),
            "version": bom.get("version", ""),
            "issues": [],
            "warnings": [],
            "summary": {},
        }

        total_cost = 0.0
        total_power = 0.0
        component_count = 0

        for module in bom.get("modules", []):
            for comp in module.get("components", []):
                component_count += 1
                cost = comp.get("unit_price", 0) * comp.get("quantity", 0)
                total_cost += cost

                # 检查停产状态
                status = comp.get("status", "active")
                if status == "discontinued":
                    alts = comp.get("alternatives", [])
                    report["issues"].append({
                        "level": "high",
                        "component": comp["code"],
                        "name": comp["name"],
                        "issue": "元器件已停产",
                        "suggestion": f"替代物料: {', '.join(alts)}" if alts else "无替代物料，需重新选型",
                    })
                elif status == "warning":
                    report["warnings"].append({
                        "level": "medium",
                        "component": comp["code"],
                        "name": comp["name"],
                        "issue": comp.get("status_note", "存在风险标记"),
                        "suggestion": f"替代物料: {', '.join(comp.get('alternatives', []))}",
                    })

                # 检查供应商可用性
                for sc in comp.get("supplier_codes", []):
                    if sc in suppliers:
                        s = suppliers[sc]
                        if s.get("level") == "D":
                            report["issues"].append({
                                "level": "high",
                                "component": comp["code"],
                                "issue": f"供应商{sc}({s['name']})已被淘汰",
                                "suggestion": "需更换供应商",
                            })
                        if s.get("risk_flags"):
                            for flag in s["risk_flags"]:
                                report["warnings"].append({
                                    "level": "medium",
                                    "component": comp["code"],
                                    "issue": f"供应商{sc}风险: {flag}",
                                    "suggestion": "关注并评估影响",
                                })

                # 独家供应检查
                if len(comp.get("supplier_codes", [])) == 1:
                    report["warnings"].append({
                        "level": "medium",
                        "component": comp["code"],
                        "name": comp["name"],
                        "issue": "独家供应风险 — 仅一家供应商",
                        "suggestion": "建议寻找备选供应商",
                    })

        # 功率校验
        max_power = bom.get("max_power_watts", 0)
        power_budget = bom.get("power_budget_watts", 0)
        if max_power > 0 and power_budget > 0:
            load_ratio = power_budget / max_power
            power_rule = next((r for r in rules if r["id"] == "SR-003"), None)
            max_ratio = power_rule["params"]["max_load_ratio"] if power_rule else 0.8
            if load_ratio > max_ratio:
                report["issues"].append({
                    "level": "high",
                    "issue": f"功率超标: 预估{power_budget}W / 额定{max_power}W = {load_ratio:.0%}，超过{max_ratio:.0%}上限",
                    "suggestion": "需降低功耗或升级电源模块",
                })

        report["summary"] = {
            "total_components": component_count,
            "estimated_cost": round(total_cost, 2),
            "issues_count": len(report["issues"]),
            "warnings_count": len(report["warnings"]),
            "verdict": "PASS" if not report["issues"] else "FAIL",
        }

        return json.dumps(report, ensure_ascii=False, indent=2)
