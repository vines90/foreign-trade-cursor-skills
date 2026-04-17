# 首次建表流程（lark-cli v1.0.9+ / Base v3 API）

> 仅在 `.cursor/state/bitable.json` 不存在或 `app_token` 为空时执行。
> 执行完毕后，必须把所有 token / id / field_id 写回 `bitable.json`。

> **强烈建议**：直接复用 `output/raw/setup_bitable.py` 一次性脚本（约 30 秒跑完），
> 而不是手工拼 30+ 条 `field-create` 命令。脚本已经处理好下面所有踩坑点。

---

## 关键 API 差异速查（v3 必读）

下面这些和老版 lark-cli 文档不一样，照着老文档写 100% 失败：

| 项目 | ❌ 老写法 | ✅ v3 正确 |
|---|---|---|
| 全局 flag | `--app-token` | `--base-token` |
| 字段类型 | 数字 `1/3/5/15/21` | 字符串枚举 `text/select/datetime/url/link/...` |
| 单选 options | `--property '{"options":[...]}'` | 顶层 `--json '{"options":[...]}'` |
| 多选 select | type=4 | type=`select` + 顶层 `multiple: true` |
| 关联字段 | type=21 + `property.table_id` | type=`link` + 顶层 `link_table` + `bidirectional: true` |
| URL 字段 | type=15 | type=`url`（实际存储为 text） |
| 自动编号 | type=1005 | type=`auto_number`（新建表会自动给一个 ID 字段） |
| 删除字段 | `+field-delete` | 必须加 `--yes` 否则报 unsafe_operation_blocked |
| 删除记录 | `+record-delete` | 同上必须 `--yes` |
| 创建记录响应 | `data.records[].record_id` | `data.record_id_list[]` |
| 列出记录响应 | `data.items[].fields` | `data.data[]`（值数组）+ `data.field_id_list[]` + `data.record_id_list[]` |

字段类型完整字符串枚举（v3 only）：

```
text | number | select | datetime | created_at | updated_at
user | created_by | updated_by | link | url | formula | lookup
auto_number | attachment | location | checkbox | phone
```

---

## 前置检查

```bash
lark-cli auth whoami
# 未登录 / token 失效:
lark-cli auth login --as user
```

---

## Step 1: 创建 Base

```bash
lark-cli base +base-create --name "外贸客户开发" --time-zone "Asia/Shanghai"
```

返回 `data.base.base_token`，记下作为 `$APP`。
URL 模板：`https://lcnctb2235nb.feishu.cn/base/<base_token>`

---

## Step 2: 处理默认表

新建 base 会自带一张「数据表」，里面有 4 个默认字段：
`单选 / 日期 / 附件 / 文本`

策略：
- 把它改名为「客户主表」
- 找到 `type=text` 的那个字段（默认叫"文本"），改名为"公司名称"作为主键
- 删除剩下 3 个无用默认字段（必须加 `--yes`）
- 加业务字段

```bash
APP=<base_token>
TBL=<default_table_id>  # 通过 +table-list 拿

lark-cli base +table-update --base-token $APP --table-id $TBL --name "客户主表"
lark-cli base +field-update --base-token $APP --table-id $TBL \
  --field-id <text_field_id> \
  --json '{"name":"公司名称","type":"text"}'
lark-cli base +field-delete --base-token $APP --table-id $TBL \
  --field-id <other_field_id> --yes
```

⚠️ 主键字段（首列）通常不能 `+field-delete`，会提示主键保护。
⚠️ `+field-update` 如果新值与现值完全一致，会返回 `800070003 no operation produced`。先 `+field-list` 检查再决定要不要更新。

---

## Step 3: 创建另两张表

```bash
lark-cli base +table-create --base-token $APP --name "联系人表"
lark-cli base +table-create --base-token $APP --name "开发日志"
```

新表自带一个 `auto_number` 类型的 `ID` 字段（不是 text），无法转成主键文本字段。
解决：再 `+field-create` 一个 `name=姓名 / 主题 / type=text` 字段做业务展示主键，
原 `ID` 字段保留作为内部唯一编号。

---

## Step 4: 创建字段（v3 JSON 格式）

### 文本 / 数字 / 复选框

```json
{"name":"城市","type":"text"}
{"name":"成立年份","type":"number"}
{"name":"是否决策人","type":"checkbox"}
```

### URL（注意：实际存储为 text，写值时直接传字符串）

```json
{"name":"公司官网","type":"url"}
```

### 单选

```json
{"name":"客户状态","type":"select",
 "options":[
   {"name":"待开发","color":0},
   {"name":"已发首信","color":1}
 ]}
```

### 多选

```json
{"name":"销售渠道","type":"select","multiple":true,
 "options":[{"name":"B2B","color":0},{"name":"OEM","color":1}]}
```

### 日期

```json
{"name":"背调日期","type":"datetime"}
```

format 不能在创建时传，默认 `yyyy/MM/dd`。

### 双向关联（v3 关键改动！）

```json
{"name":"所属公司","type":"link",
 "link_table":"<目标表 table_id>",
 "bidirectional":true}
```

⚠️ 不能传 `multiple` 字段（会报 unrecognized key）。
⚠️ 必须传 `link_table` 字符串（不是 `property.table_id`）。
✅ `bidirectional:true` 会自动在目标表生成对侧关联字段。

### Lookup（查找引用）

`type: "lookup"`，需要先有 `link` 字段做基础。脚本里暂未自动建，
推荐建表跑通后通过飞书 UI 手动加（更直观）。

---

## Step 5: 命令调用模板

```bash
lark-cli base +field-create \
  --base-token $APP \
  --table-id $TBL \
  --json '<上面对应 JSON>'
```

成功响应：

```json
{
  "ok": true,
  "data": {
    "created": true,
    "field": {
      "id": "fldXXXXX",       // 注意：是 id，不是 field_id
      "name": "客户状态",
      "type": "select",
      ...
    }
  }
}
```

---

## Step 6: 写入记录（batch-create）

```bash
lark-cli base +record-batch-create \
  --base-token $APP \
  --table-id $TBL \
  --json '{
    "fields": ["公司名称","客户状态","所属公司"],
    "rows": [
      ["ACME GmbH","待开发", ["recXXXXX"]]
    ]
  }'
```

注意：
- `fields` 数组用**字段名**（中文），不是 field_id
- `rows[i]` 是值数组，顺序必须严格对应 `fields`
- 多选字段值用 `["A","B"]`
- 关联字段值用 `["recXXXXX"]`（关联记录 ID 数组）
- 日期字段用毫秒时间戳（如 `1776441080712`），不是 ISO 字符串

成功响应：

```json
{
  "ok": true,
  "data": {
    "record_id_list": ["recvh42bnTzFy4", "recvh42bnTFl0g"],  // ← 拿这个！
    "field_id_list": [...],
    "data": [["ACME GmbH","待开发",["recXXXXX"]]]
  }
}
```

---

## Step 7: 写状态文件

把所有 token / table_id / 关键 field_id 写到：

```
.cursor/state/bitable.json
```

格式见 `state.json.example`。

---

## Step 8: 输出 Bitable URL

```
https://lcnctb2235nb.feishu.cn/base/<base_token>
```

---

## 错误处理速查

| 错误码 | 原因 | 修复 |
|---|---|---|
| `800010608` Path param "recordId" has an invalid format | shell 把多个 ID 拼一起传了 | 用 Python subprocess 单条调用，或仔细引用 |
| `800010701` Invalid discriminator value | type 用了数字 | 改成字符串 `text/select/...` |
| `800010701` Unrecognized key(s) in object: 'property' | 字段属性放 property 下 | 平铺到顶层 |
| `800010701` Unrecognized key(s) in object: 'multiple' | link 字段传了 multiple | 删掉，link 用 bidirectional |
| `800010701` link_table: Provide a value of type string | type=link 没传 link_table | 顶层加 `"link_table":"<table_id>"` |
| `800070003` no operation produced | field-update 新值=现值 | 先 list 检查，再决定是否更新 |
| `unsafe_operation_blocked` | delete 类操作 | 加 `--yes` |
| `actor-memory-limit-exceeded` | Apify 并发超限 | 顺序跑或拆批次 |

---

## 幂等性

- 重复执行 setup 不应破坏已有数据
- 检查策略：先 `+table-list` → 如果 3 张表都已存在则跳过
- 字段层面：`+field-list` → 按 name 匹配，已存在则跳过 `+field-create`
- 记录层面：业务上必须先 `+record-search` 按官网/邮箱去重
