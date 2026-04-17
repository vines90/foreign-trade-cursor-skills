---
name: bitable-trade-devlog
description: 将外贸客户开发的每一次互动（开发信发送、客户回复、电话会议、寄样、报价、合同等）记录到飞书多维表「开发日志」表，并按规则自动联动更新客户主表的状态。当用户提到"记录开发日志"、"记客户回信"、"跟进日志"、"记一次互动"、"客户回复了"、"寄样记录"、"报价记录"、"合同记录"时使用。
---

# 客户开发日志（飞书多维表）

记录外贸客户的每一次互动到飞书多维表「开发日志」表，并按状态机自动联动更新客户主表。

## 适用范围

- **触发场景**：发出开发信、收到客户回复、电话/会议、寄样、报价单、合同
- **输入**：互动事件（包含客户标识 + 互动元数据）
- **输出**：开发日志新增 1 条记录 + 可能的客户状态变更
- **不适用**：背调入库（用 `bitable-trade-customer`）；查询历史日志（直接看 Bitable 视图）

## 依赖

- `bitable-trade-customer` skill（必须已执行过 setup，状态文件存在）
- `lark-base` skill（lark-cli 已登录）
- 共享状态：`.cursor/state/bitable.json`

## 工作流

```
Task Progress:
- [ ] Step 0: 加载状态文件
- [ ] Step 1: 解析互动输入
- [ ] Step 2: 定位客户记录（必须）+ 联系人记录（可选）
- [ ] Step 3: 写入开发日志
- [ ] Step 4: 评估状态联动
- [ ] Step 5: 更新客户主表（如需要）
- [ ] Step 6: 输出结果与下一步建议
```

### Step 0: 加载状态文件

```bash
test -f .cursor/state/bitable.json || echo "ERROR: 请先调用 bitable-trade-customer skill 完成首次建表"
cat .cursor/state/bitable.json
```

提取：
- `app_token`
- `tables.devlog.table_id`
- `tables.customers.table_id`

### Step 1: 解析互动输入

至少需要：

```yaml
customer_identifier:           # 必填，三选一
  company_name: "ACME GmbH"    # 推荐
  # 或
  website: "https://acme.de"
  # 或
  customer_record_id: "recXXX"

interaction:
  type: "📧首封开发信"          # 必填，按 schema 选项
  direction: "⬆️发出"           # 必填
  date: "2026-04-17 10:30"     # 必填，缺失则用当前时间

content:
  subject: "..."               # 邮件 subject
  summary: "..."               # 1-3 句话
  full_content: "..."          # 邮件原文（可选）
  message_id: "<...>"          # SMTP Message-ID（可选）
  attachments: []              # 附件路径

contact_email: "buyer@acme.de"  # 可选，用来定位联系人记录

signals:
  sentiment: "😊积极"           # 可选
  key_signals: ["询价", "索样"]  # 可选

next_action:
  date: "2026-04-22"           # 可选
  description: "回复样品价格"
```

#### 输入来源约定
- 来自 `auto-smtp-email` 发送 → `direction=⬆️发出`，type 由用户/上游指定
- 来自人工粘贴回复邮件 → `direction=⬇️收到`，需 LLM 提取 sentiment / signals

### Step 2: 定位客户和联系人记录

#### 2.1 定位客户

按 `customer_identifier` 优先级查询：

```bash
# 按公司名
lark-cli base +record-search \
  --app-token <app_token> \
  --table-id <customers_table_id> \
  --filter '{"conjunction":"and","conditions":[{"field_name":"公司名称","operator":"is","value":["ACME GmbH"]}]}'
```

- **找到** → 取 `record_id`
- **未找到** → 中止并提示用户："客户不存在，请先用 `bitable-trade-customer` 入库"

#### 2.2 定位联系人（可选）

如果提供了 `contact_email`：

```bash
lark-cli base +record-search \
  --app-token <app_token> \
  --table-id <contacts_table_id> \
  --filter '{"conjunction":"and","conditions":[{"field_name":"邮箱","operator":"is","value":["buyer@acme.de"]}]}'
```

- 找到 → 关联进日志
- 未找到 → 提示用户是否新增；不新增也可以（联系人字段非必填）

### Step 3: 写入开发日志

```bash
lark-cli base +record-create \
  --app-token <app_token> \
  --table-id <devlog_table_id> \
  --fields '{
    "所属客户": [{"record_ids":["<customer_record_id>"]}],
    "联系人":   [{"record_ids":["<contact_record_id>"]}],
    "互动类型": "📧首封开发信",
    "方向":    "⬆️发出",
    "互动日期": "2026-04-17 10:30",
    "主题":    "Quick introduction from XXX",
    "内容摘要": "首封介绍长期包装产品，针对礼盒/礼袋切入",
    "完整内容": "Hello...",
    "邮件 Message-ID": "<abc@163.com>",
    "客户情绪": "❓未知",
    "关键信号": ["询价"],
    "下次跟进日期": "2026-04-22",
    "下一步动作": "5 天无回复则发跟进邮件",
    "客户状态变更": "待开发→已发首信"
  }'
```

记录返回的 `log_record_id`。

### Step 4: 评估状态联动

读取 [`references/status-rules.md`](references/status-rules.md) 的状态机规则。

实现要点：

```
当前客户状态 = 查询客户主表当前 客户状态 字段
新状态, 需确认 = compute_status_change(当前状态, 本次日志)

if 新状态 == 当前状态: 跳过 Step 5
if 需确认 == True: 询问用户 → 用户确认后才进 Step 5
if 需确认 == False: 直接进 Step 5
```

### Step 5: 更新客户主表（如需要）

```bash
lark-cli base +record-update \
  --app-token <app_token> \
  --table-id <customers_table_id> \
  --record-id <customer_record_id> \
  --fields '{"客户状态":"已发首信"}'
```

⚠️ 不要在这一步同时改其他字段（避免覆盖手工编辑）。

### Step 6: 输出结果

```markdown
## ✅ 开发日志已记录

**Bitable**: https://feishu.cn/base/<app_token>?table=<devlog_table_id>

### 本次记录
- 客户：ACME GmbH
- 互动：📧首封开发信（⬆️发出）2026-04-17 10:30
- 日志编号：L-2026-0001

### 状态变更
- 客户状态：待开发 → 已发首信 ✅

### 关键信号提示
- 包含「询价」：建议优先回复并准备报价单

### 下一步
- 已设定下次跟进日期：2026-04-22
- 5 天无回复时，可触发：调用 `auto-smtp-email` 发跟进邮件 → 完成后再调用本 skill 记录
```

## 批量场景

如果一次性要记录多条（例如 `auto-trade-customer-development` 一次发了 5 封首信）：

1. 先把 5 条互动整理成数组
2. 对每条客户分别 Step 2 定位 record_id
3. 用 `+record-batch-create` 一次性写入 5 条日志
4. 状态联动逐条评估，**只对没有冲突的批量更新客户主表**（同一客户多条日志时，按时间最新一条决定状态）

```bash
lark-cli base +record-batch-create \
  --app-token <app_token> \
  --table-id <devlog_table_id> \
  --records '[{...},{...},{...}]'
```

## 错误处理

- **客户不存在** → 不要静默创建客户，必须中止并提示用户先入库
- **状态机规则冲突**（当前状态已比目标状态更靠后）→ 跳过状态变更，仅记日志
- **关联字段格式错** → 双向关联值必须 `[{"record_ids":["..."]}]`，不是字符串数组
- **互动类型/方向/情绪不在 schema 选项中** → 报错并列出合法值，不要自动落到其他选项

## 与其他 skill 联动

| 上游事件 | 触发本 skill 写入的字段 |
|---|---|
| `auto-smtp-email` dry-run 通过 + 真实发送成功 | type=📧首封/跟进开发信, direction=⬆️发出, message_id=SMTP响应 |
| 人工粘贴客户回信 | type=📨客户回复, direction=⬇️收到, sentiment+signals 由 LLM 抽取 |
| 寄样动作 | type=📦寄样, direction=⬆️发出, 附件=快递单 |
| 用户发出报价 | type=💰报价单, direction=⬆️发出, 附件=PDF 报价单 |
| 签订合同 | type=📄合同, direction=任意, ⚠️ 触发"是否改为已成交"确认 |

## 注意事项

- ⚠️ 客户状态联动是**单向推进**，不会自动回退（避免误操作覆盖人工标注）
- 邮件 Message-ID 用于将来追踪邮件线程，能拿到就一定要存
- `下次跟进日期` 字段可被「待跟进」视图捕获，是后续提醒系统的基础
- 涉及个人信息（联系人邮箱/电话），勿在对话中明文回显完整列表，必要时只显示数量与样例
