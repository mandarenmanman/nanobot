# 太一 — 智能柜全链路AI决策中枢

> 太一生水，水生万物。太一驱动全链路，三清洞察万物理。

基于 nanobot 框架的智能柜业务 Agent 系统。

## 目录结构

```
workspace/
├── data/                    # 业务数据
│   ├── customers/           # 客户档案
│   ├── bom/templates/       # BOM模板
│   ├── suppliers/           # 供应商档案
│   ├── orders/              # 订单记录（自动生成）
│   ├── work_orders/         # 售后工单
│   ├── drawings/            # 图纸索引
│   └── rules/               # 业务规则库
├── skills/                  # Agent 技能
│   ├── dispatcher/          # AI总控调度器
│   ├── sales/               # 销售部
│   ├── hardware/            # 硬件部
│   ├── supplier/            # 供应商管理
│   ├── ops/                 # 运维部
│   └── analyst/             # 三清（监事模型）
├── tools/                   # 自定义业务工具
│   ├── bom_validate.py      # BOM校验
│   ├── order_dispatch.py    # 订单分发
│   ├── supplier_quote.py    # 供应商询价
│   └── analyst_inspect.py   # 三清巡检
└── memory/                  # nanobot 记忆系统（自动管理）
```

## 快速开始

### 1. 配置 nanobot 指向此工作空间

编辑 `~/.nanobot/config.json`：
```json
{
  "agents": {
    "defaults": {
      "workspace": "/path/to/byecho/workspace"
    }
  }
}
```

### 2. 注册业务工具

在 nanobot 启动代码中加入：
```python
from byecho.workspace.tools.register import register_byecho_tools
register_byecho_tools(agent_loop)
```

### 3. 开始使用

启动 nanobot 后，直接用自然语言下单：

```
> 客户C001要50台室内标准智能柜，带除湿和远程监控，3周内交付
```

Agent 会自动：
1. 解析需求 → 匹配BOM模板
2. 校验BOM → 排查风险
3. 创建订单 → 分发到各部门
4. 向供应商询价 → 输出比价表
5. 汇总报告 → 给出可行性评估
