---
name: bitable-trade-customer
description: 将外贸客户背调结果结构化存储到飞书多维表（外贸客户开发 Bitable）。支持首次自动建表（客户主表/联系人表/开发日志 三表关联）+ 后续增量写入。自动处理去重、关联、状态初始化。当用户提到"客户入库"、"背调存飞书"、"同步客户到多维表"、"把背调结果保存"、"创建客户档案"时使用。
---

# 客户背调入库（飞书多维表）

将 `b2b-customer-research` 或 `auto-trade-customer-development` 输出的背调结果，结构化写入飞书多维表「外贸客户开发」。

## 适用范围

- 输入：1 个或多个客户的背调结果（markdown 报告、JSON 对象、CSV 行）
- 输出：写入飞书 Bitable，返回每条记录的 record_id 和 Bitable URL
- 场景：从 0 创建客户档案；新增客户入库；批量导入历史客户

## 依赖

- `lark-base` skill（lark-cli 已登录、`+base-create / +table-create / +field-create / +record-batch-create`）
- `lark-shared`（首次需要 `lark-cli auth login --as user`）
- 上游 skill（任选其一）：`b2b-customer-research` / `auto-trade-customer-development`

## 状态文件

共享状态：`.cursor/state/bitable.json`

```jsonc
{
  "app_token": "...",          // Bitable 唯一标识
  "tables": {
    "customers": { "table_id": "...", "fields": { ... } },
    "contacts":  { "table_id": "...", "fields": { ... } },
    "devlog":    { "table_id": "...", "fields": { ... } }
  }
}
```

`bitable-trade-devlog` skill 会读取同一个文件。

## 工作流

```
Task Progress:
- [ ] Step 0: 检查/初始化 Bitable
- [ ] Step 1: 解析输入背调数据
- [ ] Step 2: 客户主表去重检查
- [ ] Step 3: 写入客户主表
- [ ] Step 4: 提取联系人 → 写入联系人表
- [ ] Step 5: 输出结果与 Bitable URL
```

### Step 0: 检查/初始化 Bitable

```bash
# 1. 检查状态文件
test -f .cursor/state/bitable.json && cat .cursor/state/bitable.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('app_token',''))"
```

- 文件存在且 `app_token` 非空 → 直接进入 Step 1
- 否则 → 严格按 [`references/setup.md`](references/setup.md) 执行首次建表流程

**首次建表前必读文档**：
- [`references/schema.md`](references/schema.md) - 三张表的完整字段定义（唯一真相源）
- [`references/setup.md`](references/setup.md) - 建表步骤与命令

**建表完成后**：必须把 `app_token`、3 个 `table_id`、关键字段的 `field_id` 写入 `.cursor/state/bitable.json`。

### Step 1: 解析输入背调数据

支持的输入格式（自动识别）：

#### 格式 A: Markdown 报告（来自 `b2b-customer-research`）
解析以下章节：
- "公司概况" → 客户主表的基础字段
- "产品与业务" → 主营产品 / 品牌 / 销售渠道
- "认证与资质" → 认证资质（多选）
- "关键联系人" → 联系人表（每行一个）
- "合作潜力评估" → 采购信号

#### 格式 B: JSON 对象
直接映射到字段，字段名按 `schema.md` 中文名。

#### 格式 C: 批量（数组）
对每条调用 Step 2-4。

### Step 2: 客户主表去重检查

去重键优先级：
1. `公司官网`（标准化：去 trailing `/`、统一 https）
2. `公司名称`（精确匹配）

```bash
# 按官网搜索
lark-cli base +record-search \
  --app-token <app_token> \
  --table-id <customers_table_id> \
  --filter '{"conjunction":"and","conditions":[{"field_name":"公司官网","operator":"is","value":["https://example.com"]}]}'
```

- **未找到** → Step 3 创建新记录
- **找到** → 询问用户：跳过 / 合并更新 / 强制新建（默认跳过）

### Step 3: 写入客户主表

字段填充规则：
- `客户状态`：默认 `待开发`
- `价值评级`：上游有评分则填 A/B/C，否则 `⚪未评级`
- `背调日期`：当前日期
- `背调来源`：根据上游 skill 判断（`b2b-customer-research` → `官网`；`auto-trade-customer-development` → `Apify-Maps + 官网` 等）
- `背调报告`：完整 markdown 原文
- 所有字段先按 `schema.md` 校验，未知值映射到对应单选/多选的最近选项；都不匹配则放 `备注`

批量写入：

```bash
lark-cli base +record-batch-create \
  --app-token <app_token> \
  --table-id <customers_table_id> \
  --records '[{"fields":{"公司名称":"...","客户状态":"待开发",...}}]'
```

记录返回的 `record_id`（联系人写入需要它做关联）。

### Step 4: 提取联系人 → 写入联系人表

对每个客户的关键联系人 + 通用邮箱：

#### 4.1 联系人去重
- 按 `所属公司 + 邮箱` 组合去重
- 找到则跳过

#### 4.2 通用邮箱处理
通用邮箱（sales@/info@/purchase@）也写入联系人表：
- `姓名` 填邮箱前缀（如 `sales`）
- `职位` 填 `通用邮箱`
- `部门` 按前缀映射：sales→销售、purchase→采购、info→未知

#### 4.3 批量写入

```bash
lark-cli base +record-batch-create \
  --app-token <app_token> \
  --table-id <contacts_table_id> \
  --records '[{"fields":{"姓名":"...","邮箱":"...","所属公司":[{"record_ids":["<customer_record_id>"]}]}}]'
```

注意双向关联字段格式：`{"record_ids":["..."]}`。

### Step 5: 输出结果

```markdown
## ✅ 客户入库完成

**Bitable**: https://feishu.cn/base/<app_token>

### 写入统计
- 客户主表：新增 X 条 / 跳过 Y 条 / 更新 Z 条
- 联系人表：新增 N 个

### 客户列表
| 公司名称 | 国家 | 评级 | record_id |
|---|---|---|---|
| ACME GmbH | DE | 🔴A | recXXXXX |
| ... | | | |

### 后续动作
- 查看客户详情：[Bitable 链接](...)
- 触发开发流程：调用 `auto-trade-customer-development`
- 记录开发日志：调用 `bitable-trade-devlog`
```

## 错误处理

- **lark-cli 未登录** → 提示 `lark-cli auth login --as user`
- **app_token 失效** → 删除 `.cursor/state/bitable.json` 后重新 Step 0
- **字段不存在** → 检查 schema 是否被手工改过；按 schema.md 重新创建缺失字段
- **关联字段格式错** → 双向关联值必须是 `{"record_ids":[...]}`，不是字符串

## 注意事项

- ⚠️ 写入前**必须**完成 Step 2 去重，避免脏数据
- 单选字段值不在 options 列表时，会被 lark-cli 报错；先 `+field-search-options` 检查
- 大批量（>50 条）时拆分多次 `+record-batch-create`，每次最多 500 条
- 客户名称、官网等核心字段不要含换行符
- 涉及个人信息（联系人邮箱/电话），勿在对话中明文回显完整列表，必要时只显示数量与样例
