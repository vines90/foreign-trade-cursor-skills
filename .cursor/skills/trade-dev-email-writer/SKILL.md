---
name: trade-dev-email-writer
description: 专门撰写外贸客户开发信（cold email）的技能。输入是客户背调报告 + 我方公司/产品信息，输出一封高度定制、贴近客户业务真实信号、不带营销硬卖腔、且能避开主流邮件服务商垃圾邮件识别规则的英文/日文/多语言开发信正文。每封邮件必须以背调结果为基础逐封重写，禁止复用通用正文模板群发。当用户提到"写开发信"、"客户开发邮件"、"针对这个客户写一封信"、"把背调结果转成邮件"、"cold email"、"outreach email"、"开发信不要营销味"、"避免被识别为垃圾邮件"时使用。
---

# 外贸开发信撰写

## 定位

这个 skill **只负责"写"**，不管发送（→ `auto-smtp-email`）、不管搜客户（→ `trade-customer-search`）、不管入库（→ `bitable-trade-customer`）。

输入：

- 一份客户背调报告（来自 `b2b-customer-research`，或用户直接粘贴的客户信息）
- 我方公司信息：`supplier_company` / `sender_name` / `sender_title` / `product_category` / `product_advantages`
- 可选：之前已发过的邮件（用于决定是首封 / 二跟 / 三跟）

输出：

- `subject`：≤ 60 字符的纯净主题
- `body_text`：80–180 词的纯文本正文（中文/英文/日文按客户语言）
- 一份"反营销腔 + 反垃圾邮件"自检清单结果
- 一段"为什么这封信只对这家客户成立"的简短说明（写在草稿文件最后注释里，或放到对话回复中）

> ⚠️ 不要在本 skill 里直接发送邮件。生成的草稿默认放到 `output/emails/drafts/<slug>.txt`，由用户或 `auto-smtp-email` 真正发送。

## 核心原则

### 1. 全定制，反模板

**判断标准（替换法测试）**：把正文里的客户公司名、品牌名、产品线全部替换成另一家公司，如果这封邮件读起来"还成立"，就是不合格，必须重写。

每封邮件必须：

- 引用**至少 2 个**只属于这家客户的具体信号（品牌、产品 SKU、近期动态、官网原话、领导人变更、展会、店铺地址 …）
- 明确说出"为什么我联系的是你这家公司，而不是隔壁那家"
- 推荐我方产品时，**只挑 1–2 个最匹配的切入点**，不罗列全部产品线

### 2. 反营销硬卖腔

我们要的是"**同行简报 / 顾问咨询 / 工厂方代表的礼貌问询**"语气，不是"销售员的全员喊单"语气。

直接禁用的措辞：

| 禁用词 / 句式 | 原因 |
|---|---|
| `Best price` / `Lowest price` / `Cheapest` | 价格诱导，垃圾邮件高频词 |
| `100% free` / `No cost` / `Risk-free` | 营销诱导词 |
| `Limited time` / `Act now` / `Hurry` | 紧迫感施压 |
| `Buy now` / `Click here` / `Order today` | 硬 CTA |
| `Guaranteed` / `Money back guarantee` | 承诺感太强 |
| `Dear Sir/Madam` / `Dear friend` / `To whom it may concern` | 一看就是群发 |
| `We are the leading manufacturer of …` | 自夸开头 |
| `We offer many kinds of … for many industries` | 大而空 |
| `Hope this email finds you well` | 烂大街开场，邮件服务商也学过 |
| 多个 `!` / 多个 `$` / 全大写主题 | 触发垃圾邮件特征 |

允许且推荐的措辞：

- `I'm reaching out because …`（说原因）
- `I noticed that …` / `I saw on your website that …`（说线索）
- `Worth a quick comparison?` / `If it's worth a 15-min call, happy to set one up.`（轻量 CTA）
- `No obligation either way.` / `Either way, kind regards.`（降低压迫感）
- `If procurement now sits with someone else, a quick steer is appreciated.`（给对方台阶）

### 3. 反"被识别为营销邮件"

写的时候同时是为了**通过 Gmail / Outlook / Yahoo / 网易企业邮的反垃圾打分**，不是只有"语义上不像营销邮件"。

详细清单见 [references/anti-spam-checklist.md](references/anti-spam-checklist.md)。最关键 8 条：

1. **主题** ≤ 60 字符，不全大写，不含 `!`、不含 `$`、不含 emoji，与正文高度匹配
2. **正文** 80–180 词，文字自然，不像新闻稿
3. **链接** ≤ 2 个；首封邮件**不要内嵌图片**，不要 tracking pixel
4. **不要 `unsubscribe` 字样**——对方又没订阅你的 newsletter
5. **签名**：邮箱域名、官网域名、From 地址三者一致；电话用国际格式
6. **HTML 与纯文本一致**：如果用了 HTML 模板，纯文本版必须包含相同信息
7. **首封邮件不要附件**（catalog/PDF 放在 CTA 里"如需可发"）
8. **不要在正文塞红色加粗、不要超过 2 段彩色字**

## 写信工作流

### Step 1：从背调报告里抽信号

打开背调报告，按下面六类**逐项**抽取（找不到就空着，但不要瞎编）：

1. **公司角色**：制造商 / 品牌方 / 经销商 / 零售商 / 礼赠服务商
2. **业务信号**：主营品类、SKU 关键词、品牌定位（premium / boutique / wholesale / D2C / corporate gifting）
3. **个人信号**：联系人姓名、职位、入职/晋升时间、LinkedIn 上写的强项
4. **官网原话**：能直接引用的一句话或一个产品名
5. **近期动态**：新店、收购、新品、参展、招商、领导人变更
6. **包装相关线索**：是否已经在卖包装、用什么材质、是否做礼盒/集装/零售陈列

至少抽到 **2 个**才能开始写。抽不到 → 回去补背调，不要硬写。

### Step 2：判断这封信的类型

| 类型 | 触发条件 | 对应写法 |
|---|---|---|
| 首封（cold） | 该客户没有任何往来 | 自我介绍 + 1 个匹配点 + 轻量 CTA |
| 第二次跟进 | 首封发出 ≥ 5 天无回 | 不重复首封，换角度（换联系人 / 换 CTA / 换素材） |
| 个人版补发 | 首封发到 info@ 没回，找到决策人邮箱 | 直接对决策人讲，提"我昨天也发了一封到 info@"，避免被当骚扰 |
| 资料补发 | 客户回复"发个 catalog" | 直接给资料，不要又一段销售话术 |

### Step 3：套结构，不套正文

结构模板见 [references/email-structures.md](references/email-structures.md)。任何一种结构都强制四段：

1. **第一段（≤ 2 句）**：说我是谁 + 为什么联系**这家**公司（必须含 ≥ 1 个客户信号）
2. **第二段（2–4 句）**：说明我方哪一个产品/能力对应他们哪一个具体场景（必须含 ≥ 1 个客户信号 + 1 个我方对应能力）
3. **第三段（≤ 3 句）**：给一个轻量 CTA，最好是二选一（A. 发 catalog/报价 / B. 寄 3–4 件样品）
4. **结尾**：礼貌台阶 + 简洁署名

### Step 4：语言与本地化

- **目标客户官网语言 = 邮件语言**。客户是日本公司用日语，是法国公司用法语（或英语），不要"反正大家都懂英语"
- 英文：商务正式偏简洁，不要美式过分热情，不要 `Hey there!`
- 日文：使用正确敬语（「お世話になっております」「ご検討のほど」），署名用「○○株式会社 海外営業部」格式
- 中文（极少用，仅在客户为华人/华裔家族企业时）：商务体，不口语化

### Step 5：自检 + 输出

写完后必须跑一遍自检：

```
[ ] 替换法测试：把公司名替换后，邮件是否还成立？（成立 = 不合格，重写）
[ ] 是否引用了 ≥ 2 个客户专属信号？
[ ] 主题 ≤ 60 字符、无全大写、无 ! 、无 $ 、无 emoji？
[ ] 正文是否 80–180 词？
[ ] 是否避免了所有禁用措辞？
[ ] 链接 ≤ 2、无内嵌图、无 tracking pixel、无 unsubscribe？
[ ] 签名域名与发信域名一致？
[ ] 是否只推荐了 1–2 个产品切入点（不是全产品列表）？
[ ] CTA 是否轻量（不是"立即购买/立即下单"）？
```

任何一条不过 → 重写对应部分，不要带 bug 输出。

### Step 6：把草稿落盘

存放路径建议：

```
output/emails/drafts/<batch>_<seq>_<slug>.txt
```

文件内容格式：

```
To: <收件人邮箱>
Cc: <可选>
Subject: <主题>

<正文>

<签名>

---
[内部备注：不要发送，仅给人看]
- 客户专属信号 1：…
- 客户专属信号 2：…
- 我方匹配卖点：…
- 自检结果：全部通过
```

> 内部备注那段在真实发送前必须删掉（`auto-smtp-email` 的 `--body-file` 默认会把整个文件当正文）。

## 写信前最少需要的信息

如果用户输入里下面字段缺失，先列出缺什么再写：

**客户侧（来自背调报告）**：

- `customer_company`（公司全称）
- `customer_role`（制造商 / 品牌方 / 渠道商 / 零售商 / 礼赠商）
- `customer_signals`（≥ 2 条具体信号）
- `recipient_email`
- `recipient_name`（如有）
- `recipient_role`（如有）
- `customer_language`（en / ja / zh / de / fr …）

**我方侧**：

- `supplier_company`
- `sender_name`
- `sender_title`
- `sender_email`（与发信域名一致）
- `product_category`（与客户匹配的那一类，不是全产品）
- `product_advantages`（最相关的 1–2 条，不是全部）
- `website`

任一项缺失，**先反问用户或回到背调**，不要先写正文。

## 与其他 skill 的衔接

| 上游 | 本 skill | 下游 |
|---|---|---|
| `b2b-customer-research` 输出的背调报告 | 写出 `output/emails/drafts/*.txt` | `auto-smtp-email` 真实发送 |
| `trade-customer-search` 输出的潜客名单 | 先要补背调，本 skill 不直接吃名单 | — |
| 用户手动给的客户网站链接 | 先要求跑 `b2b-customer-research`，再回到本 skill | — |

被 `auto-trade-customer-development` 编排时：本 skill 是"邮件正文生成"那一步的实现细节，输出仍然是草稿文件，发不发由编排器和用户决定。

## 反面示例（务必避免）

详细见 [examples/bad-examples.md](examples/bad-examples.md)。最常见三种：

1. **"通用万能体"**：`Dear Sir/Madam, We are the leading manufacturer of packaging in China …`
2. **"换名群发"**：连续 10 封邮件正文一样，只把公司名替换
3. **"硬卖体"**：`Limited time! Best price! Click here for 30% off!` —— 直接进垃圾邮件文件夹

## 正面示例

详细见 [examples/good-examples.md](examples/good-examples.md)。每个范例都标注了：

- 引用了哪几个客户信号
- 用了哪种结构
- 为什么避开了垃圾邮件特征

## 附加文档

- 不同客户类型的结构模板：[references/email-structures.md](references/email-structures.md)
- 反垃圾邮件检查清单：[references/anti-spam-checklist.md](references/anti-spam-checklist.md)
- 语气与措辞指南：[references/tone-and-language.md](references/tone-and-language.md)
- 正面示例：[examples/good-examples.md](examples/good-examples.md)
- 反面示例：[examples/bad-examples.md](examples/bad-examples.md)
