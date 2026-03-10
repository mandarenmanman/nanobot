# 三清巡检 — 太一系统监事模型定时任务

> 太一驱动执行，三清洞察万理。

每30分钟自动巡检一次。

## Active Tasks

### 三清巡检：全链路数据扫描

执行以下巡检任务：

1. 读取 `skills/analyst/SKILL.md` 了解三清的监事职责
2. **元始·洞察**（供应商巡检）：
   - 读取 `data/suppliers/registry.json`
   - 检查次品率超过2%的供应商
   - 检查交期达成率低于85%的供应商
   - 检查有风险标记的供应商
3. **灵宝·归因**（BOM与订单巡检）：
   - 遍历 `data/bom/templates/` 下所有文件
   - 检查停产元器件、独家供应风险、功率预算
   - 遍历 `data/orders/` 检查长时间pending的任务
4. **道德·进化**（知识沉淀）：
   - 汇总发现，将巡检报告写入 `data/analyst_reports/`
   - 如果发现严重问题，将关键发现追加到 `memory/MEMORY.md`

**输出要求**：用中文简要汇报发现了什么问题，给出改进建议。

## Completed

<!-- 已完成的巡检记录自动归档到 data/analyst_reports/ -->
