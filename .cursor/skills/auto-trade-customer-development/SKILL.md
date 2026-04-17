---
name: auto-trade-customer-development
description: 基于产品信息、公司信息和目标市场，全自动完成外贸客户开发流程：调用 trade-customer-search 搜索海外潜客、b2b-customer-research 做背调、评分客户价值、撰写并自动发送开发邮件、bitable-trade-customer 入库、bitable-trade-devlog 记开发日志。开发信默认按客户背调结果全定制生成，只复用邮件结构模板，不复用通用正文。当用户提到"全自动开发客户"、"自动找客户并发邮件"、"外贸客户开发自动化"、"输入产品和市场自动搜客户"、"自动背调并发送开发信"时使用。
---

# 全自动外贸客户开发

## 适用范围

- 用户只提供产品、公司和目标市场
- 需要从公开网页自主完成搜索、筛选、背调、写信、发信
- 优先使用已有 skill，而不是重复定义相同流程

## 依赖 skill（编排顺序）

| # | Skill | 职责 |
|---|---|---|
| 1 | `trade-customer-search` | 搜索潜客名单（多通道、多语言、自动去重、黑名单过滤）|
| 2 | `b2b-customer-research` | 单家深度背调（含联系人富化）|
| 3 | `bitable-trade-customer` | 客户档案入库（飞书多维表）|
| 4 | `auto-smtp-email` | 邮件发送（唯一发信入口）|
| 5 | `bitable-trade-devlog` | 开发日志 + 客户状态联动 |

底层依赖：`apify-ultimate-scraper`（被 `trade-customer-search` 调用）、`lark-base`（被两个 bitable skill 调用）。

**架构原则**：
- 本 skill 只负责"编排 + 评分 + 写信 + 决定何时真发"
- 搜索/背调/入库/发送/日志 都委派给专职 skill，不重复实现
- 任何子环节出错不影响其他环节继续推进

## 默认输入

若用户没有补充更多字段，至少从输入中整理出：

- `supplier_company`
- `sender_name`
- `sender_title`
- `product_category`
- `product_advantages`
- `target_market`

可选但强烈推荐补充：

- `target_customer_type`
- `oem_or_private_label`
- `website`
- `catalog_or_brochure`

## 默认策略

### 搜索层

- 每轮先找 `10-20` 家候选公司
- 默认客户类型优先：
  - `distributor`
  - `importer`
  - `wholesaler`
  - `dealer`

### 筛选层

- 只保留有独立官网或明确联系入口的公司
- 目录站、纯社媒页、无官网线索默认淘汰

### 发送层

- 默认只对 `高价值客户` 自动真实发送
- 中低价值客户只输出背调和邮件草稿，不自动发
- 若官网没有可用邮箱，不真实发送
- 邮件格式必须复用 `auto-smtp-email` 里的正文规则、签名文件、HTML 模板和发送命令格式
- 邮件正文必须按客户背调结果全定制生成，不允许只替换公司名后重复发送同一正文

评分规则见 [lead-scoring.md](lead-scoring.md)。

## 工作流

### 1. 结构化用户输入

先把用户提供的信息整理成：

```yaml
supplier_company:
sender_name:
sender_title:
product_category:
product_advantages:
target_market:
target_customer_type:
oem_or_private_label:
```

若 `target_customer_type` 缺失，默认使用 `distributor/importer/wholesaler`。

### 2. 自动搜索潜客

**直接调用 `trade-customer-search` skill**，不在本 skill 内重复搜索逻辑。

输入映射：

```yaml
product:        {product_category}
target_market:  {target_market}
customer_types: {target_customer_type or [distributor, importer, wholesaler]}
max_cities:     5
max_results_per_city: 30
enable_enrichment: false       # 默认关，富化由背调阶段 b2b-customer-research 按需做
budget_credits_usd: 1.0
```

输出：`output/leads/leads_{market}_{date}.json` 标准化潜客名单（统一 schema）。

把 `confidence in [high, medium]` 且 `next_step == research` 的公司送入下一步背调。

#### 2.1 数量控制策略

- 第一轮先取 `confidence=high` 的前 10 家进背调
- 背调通过率 <50% 时再补 medium 的前 10 家
- 单次任务总入背调数控制在 `15-25` 家（避免一轮跑爆 Apify 预算）

### 3. 自动背调

对 `research` 公司**直接调用 `b2b-customer-research` skill**：

- 抓首页、about、products、contact
- 提取公司定位、产品线、市场、邮箱、联系人
- 判断其是否适合当前产品切入

### 3.5 客户档案入库

**调用 `bitable-trade-customer` skill** 把背调结果写入飞书多维表「外贸客户开发」：

- 客户主表：每家公司一行（含背调摘要、来源、初始状态=待开发）
- 联系人表：每个邮箱一行（含通用邮箱）
- 自动去重：已存在的客户跳过

> 此步可选——如果用户明确说"不入库"或飞书未配置，跳过本步只输出本地文件。

### 4. 客户价值评分

根据 [lead-scoring.md](lead-scoring.md) 给每个客户评分。

默认划分：

- `A`: 高价值，优先自动发送
- `B`: 中价值，输出报告和草稿
- `C`: 低价值，记录但不发送

### 5. 生成开发邮件

对每个有邮箱的客户：

- 从背调结果提取 `2-4` 个具体客户信号
- 使用英文开发信
- 不编造客户未公开的信息
- 不使用夸张营销口吻
- 邮件正文、主题、签名、HTML 包装必须遵循 `auto-smtp-email`
- 邮件只允许复用结构模板，不允许复用正文模板

优先提取的客户信号包括：

- 品牌定位：premium / boutique / corporate gifting / wholesale / direct-to-consumer
- 产品线：jewellery / perfume / candles / gift sets / accessories / leather goods
- 礼赠场景：seasonal gifting / wedding / anniversary / personalization / discovery sets
- 包装线索：gift boxes / rigid boxes / pouches / bags / displays / presentation quality
- 渠道线索：wholesale / corporate orders / b2b / concierge / stockist / trade enquiries

邮件必须包含：

- 你是谁
- 你的公司和产品方向
- 为什么你联系的是这家公司
- 1-2 个最 relevant 卖点
- 轻量 CTA

正文格式强制要求：

- 主题简短直接，不使用夸张营销词
- 正文控制在 `80-180` 英文词
- 第一段说明你是谁、为什么联系对方
- 第二段只强调 `1-2` 个与客户背调直接相关的卖点
- 结尾只保留 `1` 个清晰 CTA
- 正文只生成 `body_text`，不要自行发明额外 HTML 结构
- 第一段必须提到客户真实存在的品牌、产品线、礼赠场景或渠道线索
- 第二段必须写清 `Long Term Pack` 的哪类包装适合对方，而不是泛泛列产品
- 如果正文把公司名替换后仍适用于其他客户，视为不合格，必须重写

默认邮件资产：

- 签名：`auto-smtp-email/templates/signature.txt`
- HTML 模板：`auto-smtp-email/templates/basic.html`

默认模板变量：

- `company_name`
- `email_title`
- 需要时可补充 `sender_name`

全定制质量检查：

1. 是否提到了客户官网中真实存在的业务信号？
2. 是否根据客户类型调整了口吻？
   - 品牌方：强调品牌呈现、礼赠、包装调性
   - 渠道商：强调 complementary sourcing、OEM backup、material options
   - corporate gifting：强调 seasonal projects、gift presentation、multi-format packaging
3. 是否只推荐了最相关的 `1-2` 个包装切入点？
4. 是否避免了“我们做很多包装，适合很多行业”这类泛化表述？
5. 是否避免与前一封邮件正文高度重复？

### 6. 自动发送

仅对满足以下全部条件的客户自动发送：

- 评级为 `A`
- 找到有效邮箱
- 客户类型与产品方向匹配
- 邮件正文已通过全定制检查，不是半定制或模板群发

发送时调用 `auto-smtp-email`，默认使用：

- `templates/signature.txt`
- `templates/basic.html`

执行要求：

1. 先按 `auto-smtp-email` 的方式生成 `subject`、`body_text`、收件人邮箱
2. 默认先用 `--dry-run` 预览
3. 用户明确要求发送，或当前任务本身就是“直接发送”时，再真实发送
4. 发送命令优先使用：

```bash
python3 scripts/send_email.py \
  --env-file references/credentials.env \
  --to "buyer@example.com" \
  --subject "Quick introduction from XXX" \
  --body-file /tmp/mail.txt \
  --signature-file templates/signature.txt \
  --html-template-file templates/basic.html \
  --var company_name="ACME" \
  --var email_title="Product Introduction"
```

不要只发纯文本命令，除非用户明确要求不用 HTML 模板。

### 6.5 开发日志记录

每次成功发送（不含 dry-run）后，**调用 `bitable-trade-devlog` skill** 记录互动：

- `互动类型 = 📧首封开发信`
- `方向 = ⬆️发出`
- `主题 / 内容摘要 / 完整内容` 来自本步发送的邮件
- `邮件 Message-ID` 来自 SMTP 返回
- skill 内部会自动把客户主表的`客户状态`从`待开发`改为`已发首信`

> 此步可选——飞书未配置时跳过，但会在最终输出里提示用户"未入库，建议手工跟进"。

### 7. 输出最终结果

最终输出必须分成 5 部分：

1. 搜索摘要（来自 `trade-customer-search` 的统计）
2. 客户分级结果（A/B/C 分布）
3. 背调报告摘要
4. 邮件发送结果（已发 / 仅草稿 / 未发原因）
5. 飞书入库 + 日志写入结果（含 Bitable URL）

## 输出模板

```markdown
# 外贸客户开发结果

## 1. 输入摘要
- 产品：
- 公司：
- 目标市场：

## 2. 搜索结果
- 候选公司数：
- 进入背调数：
- 高价值客户数：

## 3. 高价值客户
| 公司 | 国家/城市 | 官网 | 邮箱 | 评级 | 是否已发送 |
|------|------|------|------|------|------|

## 4. 背调摘要
- 公司 A：
- 公司 B：

## 5. 发信结果
- 已发送：
- 仅生成草稿：
- 未发送原因：

## 6. 飞书入库 + 日志
- Bitable URL：
- 客户主表新增：X 条 / 跳过：Y 条
- 联系人新增：N 个
- 开发日志新增：M 条（首封开发信）
- 已自动状态变更：X 个客户「待开发 → 已发首信」
```

## 执行规则

- 尽量全自动，不在每一步都向用户确认
- 但不要为了自动化牺牲准确性
- 找不到有效邮箱时，不强行发信
- 高价值客户数量过多时，优先发送最匹配、最容易写出全定制正文的前 `3-5` 家
- 若公开信息不足，明确标记原因
- 若涉及真实发送，邮件格式必须先对齐 `auto-smtp-email` skill，再执行发送
- 若客户背调信号不足以支撑全定制开发信，应先补背调，再决定是否发送

## 示例

参考 [examples.md](examples.md)。
