"""监事巡检工具 — 自动扫描供应商、BOM、订单、工单数据，输出异常发现"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool


class AnalystInspectTool(Tool):
    """三清巡检工具：洞察全链路数据，发现异常并输出报告。"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.data_dir = workspace / "data"

    @property
    def name(self) -> str:
        return "analyst_inspect"

    @property
    def description(self) -> str:
        return (
            "三清巡检：元始洞察供应商风险，灵宝归因BOM与订单异常，"
            "道德沉淀知识。扫描全链路数据发现次品率超标、停产元器件、"
            "独家供应风险、高频故障等，输出巡检报告并保存。"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "scope": {
                    "type": "string",
                    "description": "巡检范围",
                    "enum": [
                        "supplier",
                        "bom",
                        "orders",
                        "work_orders",
                        "all",
                    ],
                },
            },
            "required": ["scope"],
        }

    async def execute(self, scope: str) -> str:
        findings: list[dict] = []
        now = datetime.now()

        if scope in ("supplier", "all"):
            findings.extend(self._inspect_suppliers())
        if scope in ("bom", "all"):
            findings.extend(self._inspect_bom())
        if scope in ("orders", "all"):
            findings.extend(self._inspect_orders())
        if scope in ("work_orders", "all"):
            findings.extend(self._inspect_work_orders())

        report = {
            "inspection_date": now.isoformat(),
            "scope": scope,
            "total_findings": len(findings),
            "critical": [f for f in findings if f.get("severity") == "high"],
            "warnings": [f for f in findings if f.get("severity") == "medium"],
            "info": [f for f in findings if f.get("severity") == "low"],
            "findings": findings,
        }

        # 保存报告
        report_dir = self.data_dir / "analyst_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{now.strftime('%Y-%m-%d')}_sanqing_{scope}.json"
        report_path = report_dir / filename
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # 生成摘要
        summary_lines = [
            f"三清巡检 [{scope}] — {now.strftime('%Y-%m-%d %H:%M')}",
            f"发现 {len(report['critical'])} 个严重问题, "
            f"{len(report['warnings'])} 个警告, "
            f"{len(report['info'])} 个信息",
        ]
        for f in report["critical"]:
            summary_lines.append(f"  🔴 {f.get('issue', '')}")
        for f in report["warnings"][:5]:
            summary_lines.append(f"  🟡 {f.get('issue', '')}")

        summary_lines.append(f"\n报告已保存: data/analyst_reports/{filename}")
        return "\n".join(summary_lines)

    def _inspect_suppliers(self) -> list[dict]:
        findings = []
        path = self.data_dir / "suppliers" / "registry.json"
        if not path.exists():
            return findings

        reg = json.loads(path.read_text(encoding="utf-8"))
        for s in reg.get("suppliers", []):
            m = s.get("metrics", {})
            code = s["code"]
            name = s["name"]

            if m.get("defect_rate", 0) > 0.02:
                findings.append({
                    "category": "supplier",
                    "severity": "high",
                    "target": code,
                    "issue": f"供应商{name}({code})次品率"
                             f"{m['defect_rate']:.1%}，超过2%阈值",
                    "recommendation": "建议降级并启动替代寻源",
                })

            if m.get("on_time_rate", 1) < 0.85:
                findings.append({
                    "category": "supplier",
                    "severity": "medium",
                    "target": code,
                    "issue": f"供应商{name}({code})交期达成率"
                             f"{m['on_time_rate']:.0%}，低于85%",
                    "recommendation": "关注交期风险，考虑备选方案",
                })

            for flag in s.get("risk_flags", []):
                findings.append({
                    "category": "supplier",
                    "severity": "medium",
                    "target": code,
                    "issue": f"供应商{name}({code})风险标记: {flag}",
                    "recommendation": "评估影响范围",
                })

        return findings

    def _inspect_bom(self) -> list[dict]:
        findings = []
        templates_dir = self.data_dir / "bom" / "templates"
        if not templates_dir.exists():
            return findings

        supplier_path = self.data_dir / "suppliers" / "registry.json"
        suppliers = {}
        if supplier_path.exists():
            reg = json.loads(supplier_path.read_text(encoding="utf-8"))
            suppliers = {s["code"]: s for s in reg.get("suppliers", [])}

        for bom_file in templates_dir.glob("*.json"):
            bom = json.loads(bom_file.read_text(encoding="utf-8"))
            cabinet = bom.get("cabinet_type", bom_file.stem)

            for module in bom.get("modules", []):
                for comp in module.get("components", []):
                    code = comp.get("code", "?")

                    if comp.get("status") == "discontinued":
                        findings.append({
                            "category": "bom",
                            "severity": "high",
                            "target": code,
                            "issue": f"[{cabinet}] 元器件{code}已停产",
                            "recommendation": "立即替换: "
                                + ", ".join(comp.get("alternatives", [])),
                        })
                    elif comp.get("status") == "warning":
                        findings.append({
                            "category": "bom",
                            "severity": "medium",
                            "target": code,
                            "issue": f"[{cabinet}] 元器件{code}: "
                                     f"{comp.get('status_note', '风险标记')}",
                            "recommendation": "关注并准备替代方案",
                        })

                    if len(comp.get("supplier_codes", [])) == 1:
                        sc = comp["supplier_codes"][0]
                        sname = suppliers.get(sc, {}).get("name", sc)
                        findings.append({
                            "category": "bom",
                            "severity": "medium",
                            "target": code,
                            "issue": f"[{cabinet}] 元器件{code}独家供应"
                                     f"（仅{sname}）",
                            "recommendation": "寻找备选供应商降低风险",
                        })

            # 功率检查
            budget = bom.get("power_budget_watts", 0)
            max_pw = bom.get("max_power_watts", 0)
            if max_pw and budget / max_pw > 0.75:
                findings.append({
                    "category": "bom",
                    "severity": "medium" if budget / max_pw <= 0.8 else "high",
                    "target": cabinet,
                    "issue": f"[{cabinet}] 功率预算{budget}W/"
                             f"{max_pw}W={budget/max_pw:.0%}，接近上限",
                    "recommendation": "评估是否需要升级电源模块",
                })

        return findings

    def _inspect_orders(self) -> list[dict]:
        findings = []
        orders_dir = self.data_dir / "orders"
        if not orders_dir.exists():
            return findings

        now = datetime.now()
        for f in orders_dir.glob("*.json"):
            order = json.loads(f.read_text(encoding="utf-8"))
            for dept, task in order.get("tasks", {}).items():
                if task.get("status") == "pending":
                    created = order.get("created_at", "")
                    if created:
                        try:
                            age = now - datetime.fromisoformat(created)
                            if age.days > 3:
                                findings.append({
                                    "category": "order",
                                    "severity": "medium",
                                    "target": order.get("order_id", f.stem),
                                    "issue": f"订单{order.get('order_id')}"
                                             f"的{dept}任务已pending {age.days}天",
                                    "recommendation": "跟进任务进度",
                                })
                        except (ValueError, TypeError):
                            pass
        return findings

    def _inspect_work_orders(self) -> list[dict]:
        findings = []
        wo_dir = self.data_dir / "work_orders"
        if not wo_dir.exists():
            return findings

        fault_counts: dict[str, int] = {}
        component_faults: dict[str, int] = {}

        for f in wo_dir.glob("*.json"):
            if f.name == ".gitkeep":
                continue
            wo = json.loads(f.read_text(encoding="utf-8"))
            ft = wo.get("fault_type", "未分类")
            fault_counts[ft] = fault_counts.get(ft, 0) + 1
            if comp := wo.get("component"):
                component_faults[comp] = component_faults.get(comp, 0) + 1

        for ft, count in sorted(
            fault_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]:
            if count >= 3:
                findings.append({
                    "category": "work_order",
                    "severity": "high" if count >= 5 else "medium",
                    "target": ft,
                    "issue": f"高频故障: {ft} 出现{count}次",
                    "recommendation": "溯源根因，更新标准处理流程",
                })

        for comp, count in sorted(
            component_faults.items(), key=lambda x: x[1], reverse=True
        )[:3]:
            if count >= 2:
                findings.append({
                    "category": "work_order",
                    "severity": "medium",
                    "target": comp,
                    "issue": f"元器件{comp}反复出现故障（{count}次）",
                    "recommendation": "溯源到供应商和BOM，评估替换",
                })

        return findings
