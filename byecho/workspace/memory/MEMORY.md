# Long-term Memory

This file stores important information that should persist across sessions.

## User Information

(Important facts about the user)

## Preferences

(User preferences learned over time)

## Project Context

(Information about ongoing projects)

## Important Notes

(Things to remember)

---

## 监事巡检关键发现 (2026-03-10 17:47 三清巡检)

### 高风险问题（需主轮决策时参考）

1. **S005 东莞精密五金 - 供应商降级建议**
   - 次品率 2.3% 超过 2% 阈值
   - 风险标记：微动开关批次故障率偏高
   - 建议：降级为 C 级，暂停微动开关新订单
   - 影响 BOM：SW-MICRO-01

2. **SW-MICRO-01 微动开关 - 紧急切换**
   - 状态：warning
   - 原因：S005 批次故障率偏高
   - 建议：立即切换至替代型号 SW-MICRO-02

3. **S007 宁波制冷科技 - 独家供应风险**
   - 除湿片 (DH-TEC-60W) 为独家供应
   - 建议：启动第二供应商寻源，建立 3 个月安全库存

4. **功率预算警戒**
   - 当前使用率：81.8% (180W/220W)
   - 阈值：75%
   - 建议：新增功能时需严格评估功率余量

### 待办事项追踪
- [ ] P0: 暂停 S005 微动开关新订单 (截止：2026-03-12)
- [ ] P0: 切换 BOM 至 SW-MICRO-02 (截止：2026-03-15)
- [ ] P1: S005 降级评估 (截止：2026-03-20)
- [ ] P1: 除湿片第二供应商寻源 (截止：2026-03-31)

---

*This file is automatically updated by nanobot when important information should be remembered.*
