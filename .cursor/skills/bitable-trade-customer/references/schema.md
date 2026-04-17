# 外贸客户开发 - 多维表 Schema 定义

> 本文件是表结构唯一真相源。新增/修改字段必须先改这里，再同步到飞书。

## 飞书 Bitable 字段类型对照（v3 API：用字符串枚举，不要再用数字）

| 字符串 type | 名称 | 关键属性（顶层平铺，不嵌 property） |
|---|---|---|
| `text` | 多行文本 / URL 实际存储 | — |
| `number` | 数字 | `format` 可选 |
| `select` | 单选 / 多选 | `options:[{name,color}]`，多选加 `multiple:true` |
| `datetime` | 日期 / 日期时间 | 创建时不传 format（默认 yyyy/MM/dd） |
| `checkbox` | 复选框 | — |
| `user` | 人员 | `multiple:true/false` |
| `phone` | 电话号码 | — |
| `url` | 超链接 | 实际存为 text，写入直接传字符串 |
| `attachment` | 附件 | — |
| `link` | 关联（v3 不再区分单向/双向）| `link_table:"<table_id>"` + `bidirectional:true/false` |
| `lookup` | 查找引用 | `target_field`、`target_table`，建议 UI 创建 |
| `formula` | 公式 | `formatter` |
| `location` | 地理位置 | — |
| `created_at` / `updated_at` | 创建/修改时间 | 自动 |
| `created_by` / `updated_by` | 创建/修改人 | 自动 |
| `auto_number` | 自动编号 | 新建表自动有一个 ID 字段 |

**老 v2 数字 type（1/3/5/15/21）会立即报 `Invalid discriminator value`，禁止使用。**

---

## 表 1：客户主表 (Customers)

> table_name: `客户主表`

| 字段名 | type | 选项 / 备注 | 必填 |
|---|---|---|---|
| 公司名称 | text | 主键，需保证唯一 | ✅ |
| 公司官网 | url | 写入用纯字符串 | |
| 国家 | select | DE/US/UK/JP/AU/FR/IT/ES/CA/NL/AE/MX/BR/IN/SG/TH/VN/MY/PH/ID/AU/NZ/RU/KR/ZA/Other | |
| 城市 | text | | |
| 公司类型 | select | 制造商/贸易商/分销商/零售商/进口商/批发商/品牌方/未知 | |
| 公司规模 | select | 1-10/11-50/51-200/201-500/500+/未知 | |
| 成立年份 | number | | |
| 主营产品 | text | | |
| 品牌 | text | | |
| 目标销售市场 | select(multiple) | 国家列表（同"国家"字段选项） | |
| 销售渠道 | select(multiple) | B2B/B2C/批发/零售/电商/直营/经销/OEM/ODM | |
| 认证资质 | select(multiple) | ISO9001/ISO14001/CE/UL/RoHS/FDA/REACH/FSC/BSCI/SEDEX/Other | |
| 价值评级 | select | 🔴A 高价值 / 🟡B 中价值 / 🟢C 低价值 / ⚪未评级 | |
| 客户状态 | select | 待开发/已发首信/已回复/报价中/谈判中/✅已成交/❌已流失/🟦休眠 | ✅ |
| 通用邮箱 | text | sales@/info@/purchase@ 多个用换行 | |
| 电话 | phone | | |
| LinkedIn | url | 公司主页（contacts 表存个人主页） | |
| Facebook | url | | |
| Instagram | url | | |
| 采购信号 | select(multiple) | 分销商招募/参加展会/新品发布/扩张/多语言官网/海关有进货/有RFQ | |
| 背调日期 | datetime | | |
| 背调来源 | select(multiple) | 官网/Apify-Maps/LinkedIn/Facebook/海关数据/Google搜索/Cursor-WebSearch | |
| 背调报告 | text | 完整 markdown | |
| 备注 | text | | |

---

## 表 2：联系人表 (Contacts)

> table_name: `联系人表`

| 字段名 | type | 选项 / 备注 | 必填 |
|---|---|---|---|
| ID | auto_number | 新建表自动生成，保留 | 自动 |
| 姓名 | text | 业务展示主键 | ✅ |
| 职位 | text | | |
| 所属公司 | link | link_table=客户主表, bidirectional=true | ✅ |
| 邮箱 | text | | ✅ |
| 电话 | phone | | |
| WhatsApp | text | 完整 E.164 号码，例 `+44 7700 900123` | |
| LinkedIn | url | 个人主页 URL | |
| 部门 | select | 采购/销售/技术/管理/市场/客服/老板 | |
| 是否决策人 | checkbox | | |
| 优先级 | select | 高/中/低 | |
| 邮件偏好语言 | select | EN/DE/FR/ES/JP/CN/RU/PT/IT | |
| 备注 | text | | |

---

## 表 3：开发日志 (Development Log)

> table_name: `开发日志`

| 字段名 | type | 选项 / 备注 | 必填 |
|---|---|---|---|
| ID | auto_number | 新建表自动生成 | 自动 |
| 主题 | text | 业务展示主键（邮件标题） | ✅ |
| 所属客户 | link | link_table=客户主表, bidirectional=true | ✅ |
| 联系人 | link | link_table=联系人表, bidirectional=true | |
| 互动类型 | select | 📧首封开发信/📧跟进邮件/📨客户回复/📞电话/🎥视频会议/💬WhatsApp/📦寄样/💰报价单/📄合同/📅展会面谈/📝其他 | ✅ |
| 方向 | select | ⬆️发出 / ⬇️收到 | ✅ |
| 互动日期 | datetime | 写入用毫秒时间戳 | ✅ |
| 内容摘要 | text | | |
| 完整内容 | text | | |
| 邮件 Message-ID | text | SMTP Message-ID 或 In-Reply-To | |
| 客户情绪 | select | 😊积极/😐中立/😞消极/❓未知 | |
| 关键信号 | select(multiple) | 询价/索样/讨论MOQ/讨论付款/讨论物流/反对意见/已合同/拒绝/无人响应 | |
| 下次跟进日期 | datetime | | |
| 下一步动作 | text | | |
| 客户状态变更 | select | 不变/待开发→已发首信/已发首信→已回复/已回复→报价中/报价中→谈判中/谈判中→已成交/任意→已流失/任意→休眠 | |

---

## 视图建议

### 客户主表
- **全部**：默认表格视图
- **🔥A 级客户**：filter `价值评级=A`
- **🟡待跟进**：filter `客户状态 in (已发首信, 已回复, 报价中, 谈判中)` + sort `最近互动日期 ASC`
- **❓信息不全**：filter `通用邮箱 IS EMPTY OR 联系人数=0`
- **按国家**：分组视图，group by `国家`

### 联系人表
- **决策人**：filter `是否决策人=true`

### 开发日志
- **本周**：filter `互动日期 在本周`
- **待跟进**：filter `下次跟进日期 ≤ TODAY()` + sort `下次跟进日期 ASC`
- **客户回复**：filter `互动类型=📨客户回复`

---

## 字段命名约束

- 所有字段名使用中文，避免空格和特殊字符（除 emoji）
- 选项值使用中文 + emoji（提高可读性 + 视觉标识）
- 关联字段名以"所属"或具体实体名开头（所属公司 / 联系人）
- 时间字段统一 `日期` 后缀

---

## 数据规则

1. **去重键**
   - 客户主表：`公司官网` 优先，无官网则用 `公司名称`
   - 联系人表：`邮箱`（同公司同邮箱视为同一人）
   - 开发日志：不去重，每次互动都是新行

2. **关联自动化**
   - 联系人写入时，必须填 `所属公司` → 自动反向出现在客户的联系人列表
   - 日志写入时，`所属客户` 必填，`联系人` 可选（电话/会议可能没有具体邮件联系人）

3. **状态联动**
   - 写入"📨客户回复"日志 → 自动把客户状态改为"已回复"
   - 写入"💰报价单"日志 → 自动把客户状态改为"报价中"
   - 写入"📄合同"日志 → 提示用户确认是否改为"✅已成交"
