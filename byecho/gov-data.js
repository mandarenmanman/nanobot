// P1 数据治理详案 - 按端到端链路 × 8大部门节点
const GOV_BASE = [
  { icon: 'fas fa-sitemap', label: '组织架构', detail: '8大部门正式架构、部门负责人、上级汇报关系、岗位清单与编制人数' },
  { icon: 'fas fa-id-badge', label: '人员档案', detail: '姓名/工号/部门/岗位/联系方式，能力标签（擅长柜型/模块），权限与状态标签' },
  { icon: 'fas fa-project-diagram', label: '审批链', detail: '每个业务节点的审批人与替补审批人，跨部门协作对接人映射表' },
  { icon: 'fas fa-user-tag', label: '可分配人员池', detail: 'AI派单时的能力匹配依据：谁能接结构任务、谁能接硬件任务、按区域×技能分配' }
]

const GOV_DEPTS = [
  {
    name: '销售部',
    role: '节点1：需求入口 — 客户需求、报价、订单',
    color: 'bg-blue-600',
    accent: '#60a5fa',
    items: [
      { icon: 'fas fa-address-book', label: '客户档案', detail: '客户名称、行业、联系人、历史订单数、合作等级、偏好标签（常订柜型/价格敏感度/交期要求）' },
      { icon: 'fas fa-comments', label: '历史需求库', detail: '过往订单原始需求描述 → 结构化表单的映射关系，作为AI"需求解析"训练数据' },
      { icon: 'fas fa-file-invoice-dollar', label: '报价档案', detail: '历史报价单（柜型/配置/金额/成本/利润率），按柜型分类的标准报价模板' },
      { icon: 'fas fa-user-tie', label: '人员映射', detail: '销售人员 → 负责客户映射，销售人员 → 擅长柜型/行业标签' }
    ],
    acceptance: '验收：历史订单需求入库 ≥ 近2年全量，报价模板覆盖所有标准柜型'
  },
  {
    name: '结构设计部',
    role: '节点2：空间与图纸 — 3D图纸、结构方案、材质选型',
    color: 'bg-blue-500',
    accent: '#60a5fa',
    items: [
      { icon: 'fas fa-drafting-compass', label: '图纸库', detail: '按柜型→模块分级归档，打标签（柜型/模块/材质/场景/设计师），版本管理+变更记录必填' },
      { icon: 'fas fa-ruler-combined', label: '结构规则库', detail: '空间约束规则、材质选型规则、历史冲突记录（哪些模块组合出过问题及解决方案）' },
      { icon: 'fas fa-star', label: '黄金模板', detail: '复用率高、反馈好的成熟结构方案单独标记，记录适用条件和限制条件' },
      { icon: 'fas fa-user-cog', label: '人员映射', detail: '结构工程师 → 擅长柜型/模块标签，图纸评审人 → 审批权限' }
    ],
    acceptance: '验收：图纸入库 ≥ 近2年全量，标签覆盖率 ≥ 90%，结构规则 ≥ 20条'
  },
  {
    name: '硬件部',
    role: '节点3：电路与BOM — BOM清单、电路方案、元器件信息',
    color: 'bg-indigo-500',
    accent: '#818cf8',
    items: [
      { icon: 'fas fa-barcode', label: 'BOM主数据', detail: '统一编码（大类-小类-规格-版本），必填字段：规格/供应商/单价/起订量/交期/停产状态，BOM层级关系' },
      { icon: 'fas fa-exclamation-triangle', label: '元器件风险库', detail: '停产/即将停产清单+替代物料，价格波动大的元器件标记，历史故障率黑名单' },
      { icon: 'fas fa-bolt', label: '电路设计规则库', detail: '负载计算规则、主板与传感器兼容性矩阵、历史BOM打回记录及修改方案' },
      { icon: 'fas fa-user-cog', label: '人员映射', detail: '硬件工程师 → 擅长模块标签（电源/通信/传感器），BOM审核人 → 审批权限' }
    ],
    acceptance: '验收：BOM编码唯一率 100%，字段完整率 ≥ 95%，停产标记覆盖率 100%'
  },
  {
    name: '软件部',
    role: '节点4：控制程序与IoT — 代码库、协议文档、接口规范',
    color: 'bg-violet-500',
    accent: '#a78bfa',
    items: [
      { icon: 'fas fa-code', label: '代码与方案库', detail: '按功能模块归档（控制/通信/OTA/监控），标记适用柜型和依赖硬件版本，成熟模块标"可复用"' },
      { icon: 'fas fa-network-wired', label: 'IoT协议文档库', detail: '各柜型通信协议规范、设备端↔云端接口定义、第三方平台对接文档' },
      { icon: 'fas fa-bug', label: '软件设计规则库', detail: '协议选型规则、软件×硬件版本兼容矩阵、高频bug记录与修复方案' },
      { icon: 'fas fa-user-cog', label: '人员映射', detail: '软件工程师 → 擅长领域标签（嵌入式/云端/协议），代码评审人 → 审批权限' }
    ],
    acceptance: '验收：协议文档覆盖所有在产柜型，可复用模块标记 ≥ 15个'
  },
  {
    name: '行政部',
    role: '节点5：资源调度 — 会议记录、资源排期、审批流程',
    color: 'bg-amber-600',
    accent: '#f59e0b',
    items: [
      { icon: 'fas fa-warehouse', label: '资源台账', detail: '打样车间（设备/时段/预约）、测试设备（状态/负责人）、会议室（容量/配置/规则）' },
      { icon: 'fas fa-clipboard-list', label: '流程模板库', detail: '各类审批流程模板（打样/采购/出差），每个流程的节点、审批人、预计耗时' },
      { icon: 'fas fa-chart-bar', label: '历史审批数据', detail: '平均审批耗时、卡点环节分析，为AI优化调度提供基线数据' },
      { icon: 'fas fa-user-cog', label: '人员映射', detail: '行政人员 → 负责资源类型映射，各流程审批链中的行政节点确认' }
    ],
    acceptance: '验收：资源台账完整率 ≥ 95%，流程模板覆盖所有常规审批类型'
  },
  {
    name: '第三方供应商',
    role: '节点6：供应链 — 报价、交期、质量记录',
    color: 'bg-emerald-600',
    accent: '#34d399',
    items: [
      { icon: 'fas fa-building', label: '供应商档案', detail: '基础信息（全称/信用代码/品类/联系人）、商务信息（账期/起订量/交期/API能力）' },
      { icon: 'fas fa-medal', label: '供应商分级', detail: 'A核心/B备选/C观察/D淘汰，基于交期达成率+次品率评定，分级影响AI派单权重' },
      { icon: 'fas fa-exchange-alt', label: '历史交易数据', detail: '采购订单（物料/数量/单价/交期承诺vs实际）、来料质检记录、退货记录' },
      { icon: 'fas fa-shield-alt', label: '风险信息', detail: '是否独家供应、替代供应商编码、最近质量事故记录、绩效评分（价格/配合度）' }
    ],
    acceptance: '验收：基础信息完整率 ≥ 98%，绩效数据覆盖 ≥ 80%，分级覆盖 100%'
  },
  {
    name: '运维部门',
    role: '节点7：交付与售后 — 交付记录、IoT数据、售后工单',
    color: 'bg-orange-500',
    accent: '#fb923c',
    items: [
      { icon: 'fas fa-clipboard-check', label: '交付验收数据', detail: '按柜型定义验收检查清单（功能自检/参数核对/外观），历史交付记录与遗留问题' },
      { icon: 'fas fa-satellite-dish', label: 'IoT设备台账', detail: '已交付设备清单（编号/柜型/地点/客户/上线日期），设备状态，传感器配置' },
      { icon: 'fas fa-headset', label: '售后工单库', detail: '历史工单（故障描述/原因/方案/耗时），高频故障TOP10，常见故障标准处理流程' },
      { icon: 'fas fa-user-cog', label: '人员映射', detail: '运维/售后工程师 → 负责区域+擅长柜型标签，派单规则：按区域×技能匹配' }
    ],
    acceptance: '验收：设备台账覆盖所有已交付设备，历史工单入库 ≥ 近1年全量'
  },
  {
    name: '数据小脑',
    role: '节点8：分析基础 — 汇聚全链路数据，支撑认知轮',
    color: 'bg-orange-600',
    accent: '#ea580c',
    items: [
      { icon: 'fas fa-link', label: '全链路追溯模型', detail: '客户需求→BOM→图纸→供应商→交付设备→售后工单，端到端可追溯' },
      { icon: 'fas fa-users', label: '人员归因模型', detail: '人员→部门→任务→产出，全链路可归因，支撑绩效分析和能力画像' },
      { icon: 'fas fa-heartbeat', label: '数据质量监控', detail: '每周自动校验（完整性/一致性/关联性），按部门展示质量看板，低于90%自动告警' }
    ],
    acceptance: '验收：全链路关联模型上线，数据质量看板覆盖所有部门'
  }
]

const GOV_TIMELINE = {
  cols: ['各部门数据', '人员信息', '数据仓库'],
  rows: [
    { week: '第1-2周', cells: ['各部门摸底盘点', '全员信息采集+能力标签', '技术选型+数据模型设计'] },
    { week: '第2-3周', cells: ['各部门数据规范制定', '审批链与对接人确认', '开发部署'] },
    { week: '第3-6周', cells: ['并行清洗、归档、入库', '人员池与派单规则配置', '数据导入+校验脚本'] },
    { week: '第6-8周', cells: ['全链路关联校验+验收', '组织信息终验', '质量监控上线'] }
  ]
}
