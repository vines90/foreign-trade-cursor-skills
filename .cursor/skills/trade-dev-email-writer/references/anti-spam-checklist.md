# 反垃圾邮件检查清单

> 目标：让首封开发信通过 Gmail / Outlook / Yahoo / 网易企业邮 / 雅虎日本 的内容反垃圾打分，进收件箱而不是 Promotions 标签或垃圾箱。

## 1. 主题（Subject）

| 检查 | 要求 |
|---|---|
| 长度 | ≤ 60 字符（中日文 ≤ 30 全角字） |
| 大小写 | **不要**全大写。首字母大写或正常句首大写 |
| 标点 | **不要** `!`、不要 `?` 连续多个、不要 `$` 字符 |
| Emoji | **完全禁用**（首封） |
| 数字 | 不要 `100% off` / `Save 50%` / `$3000 deal` 这类 |
| 关键词 | 不要 `FREE`、`URGENT`、`WINNER`、`OFFER`、`PROMO` |
| 与正文匹配 | 主题里出现的词，正文必须出现，否则被识别为标题党 |

**好主题示例**（仅参考结构）：

- `Velvet boxes for <Brand> — direct factory benchmark`
- `<Brand> packaging — quick note from a Dongguan supplier`
- `Re: <对方先前邮件主题>`（二跟必须用 Re:）

**坏主题示例**：

- `🎁 BEST PRICE!! Limited time offer for you!!!`
- `URGENT: Your packaging supplier solution`
- `100% FREE samples — Click now`

## 2. 正文（Body）

| 检查 | 要求 |
|---|---|
| 长度 | 80–180 英文词 / 180–360 中日文字 |
| 段落 | 3–4 段，每段 ≤ 4 行 |
| 链接数量 | ≤ 2 个（一般是官网 + 一个具体页面） |
| 链接形式 | 用裸 URL 或自然嵌入文字，**不要** `Click here` |
| 内嵌图片 | **首封禁止**；二跟也尽量不要 |
| 附件 | **首封禁止**（包括 PDF catalog） |
| Tracking pixel | 禁用 |
| `unsubscribe` 字样 | 禁用（cold email 加 unsubscribe 反而像群发 newsletter） |
| 红色 / 加粗大段 | 禁用 |
| 表情符号 | 禁用（首封）；二跟最多 1 个，且与上下文自然 |
| 大写词 | 单词全大写最多 1 次（如品牌名） |
| 感叹号 | 全文 ≤ 1 个 |
| 美元符号 / 价格数字 | 不出现具体价格；要谈价 → 引导对方索取 |
| `urgent` / `important` 类词 | 禁用 |

## 3. 高频垃圾邮件触发词（按优先级）

**绝对禁用**：

```
free, 100% free, no cost, risk-free, money back guarantee
best price, lowest price, cheapest, save big, save up to
limited time, act now, hurry, expires today, while supplies last
buy now, order now, click here, click below, click to subscribe
winner, congratulations (营销式), you have been selected
make money fast, work from home, earn extra cash
```

**慎用**（每封邮件最多出现 1 次，且必须在自然语境）：

```
offer, deal, discount, sample, opportunity, introduction,
quote, quotation, wholesale, special, exclusive
```

> "introduction" / "quote" / "wholesale" 在 B2B 是合理词，但密度别太高。一封 150 词的邮件出现 3 次 `wholesale` 就开始像模板了。

## 4. 称呼与开头

| 禁用开头 | 说明 |
|---|---|
| `Dear Sir/Madam,` | 群发标志 |
| `Dear friend,` / `Hello dear,` | 群发标志 |
| `To whom it may concern,` | 一看就是冷模板 |
| `Hope this email finds you well.` | 烂大街，反垃圾邮件模型已经学过 |
| `I hope you are doing well in this difficult time.` | 同上 |
| `My name is X and I am writing to you from Y company.` | 自我介绍但没说为啥联系对方 |

**推荐开头**：

- `Hi <First Name>,` （已知名字）
- `Dear <Mr./Ms.> <Last Name>,` （正式 + 已知姓氏）
- `Dear <Brand> team,`（只有公司）
- `<会社名> <部署> <氏名> 様` + `お世話になっております。`（日文）

## 5. 签名

| 检查 | 要求 |
|---|---|
| 姓名 | 全名 |
| 职位 | 真实职位 |
| 公司全称 | 与官网/工商一致 |
| 邮箱 | **必须与发信地址同域名**（`yang@ltspack.com` 不能签 `yang@gmail.com`） |
| 官网 URL | 完整 `https://`，不用短链 |
| 电话 | 国际格式 `+86 769 xxx`，不要纯数字串 |
| 地址 | 一行完整地址，可帮 SPF/DKIM 之外的"真实存在感"加分 |
| 营销标签 | 禁用 `Sent from my iPhone` 之外的任何 promotional 标语 |
| 社交链接 | ≤ 1 个（如 LinkedIn 公司主页），不要列一排 IG/FB/X |

**好签名示例**：

```
Best regards,
Yang Li
Overseas Sales · Long Term Pack Ltd
yang@ltspack.com  |  https://www.ltspack.com/
Dongguan, China  ·  20 years in jewellery packaging
```

**坏签名示例**：

```
Best Best Best Price!!!
*** YANG ***
🎁 Long Term Pack 🎁 — Your Best Choice!!!
yang@gmail.com    [域名不一致]
WeChat: yang888 | WhatsApp: +86xxx | LinkedIn: ... | Facebook: ... | IG: ...
```

## 6. HTML / 文本一致性

如果用了 HTML 模板：

- 必须同时提供纯文本版（`auto-smtp-email` 的 `--body-file`）
- 纯文本版**包含相同信息**（不要 HTML 里有内容 / 文本版空着）
- 不要在 HTML 里塞隐藏文字（白底白字、`display:none`），这是 spam 黑名单的明确特征
- HTML 里 `<img>` 全部去掉（首封）；要图 → CTA 写"如需图样请告知"
- 不要 `<font color="red">`、不要超过 2 段彩色

## 7. 域名与发信侧（提醒，非本 skill 直接负责）

虽然这部分由 `auto-smtp-email` / 域名管理员负责，但写信时也要确认：

- 发信域名已配置 SPF
- 已配置 DKIM
- 推荐配置 DMARC（即使是 `p=none`）
- 不要用免费邮箱（`@gmail.com` / `@163.com` / `@qq.com`）发 B2B 开发信
- 一天对同一收件域名 ≤ 3–5 封，避免被识别为批量行为

## 8. 自检脚本（建议）

在草稿落盘前，跑一次简单的关键词扫描（伪代码）：

```python
FORBIDDEN = [
    "best price", "lowest price", "cheapest",
    "100% free", "no obligation today", "risk-free",
    "limited time", "act now", "hurry",
    "buy now", "click here", "order now",
    "dear sir/madam", "dear friend", "to whom it may concern",
    "hope this email finds you well",
]

text = open("draft.txt").read().lower()
hits = [w for w in FORBIDDEN if w in text]
assert not hits, f"Spam-trigger words found: {hits}"

# 主题特征
subject_line = ...  # 解析出 Subject:
assert len(subject_line) <= 60, "Subject too long"
assert subject_line == subject_line.lower() or not subject_line.isupper(), "All-caps subject"
assert "!" not in subject_line, "Exclamation in subject"
assert "$" not in subject_line, "Dollar sign in subject"

# 正文长度
body_words = len(body_text.split())
assert 60 <= body_words <= 220, f"Body length out of range: {body_words}"
```

不强制要求每次都跑代码，但**心里要按这个清单逐条过一遍**。

## 9. 发送频次（提醒）

- 同一收件人首封后，二跟间隔 ≥ 5 天；三跟 ≥ 10 天
- 总共 ≤ 3 次跟进，无回复就停（继续发会被人为标 spam）
- 同一公司不要短时间内对 3 个以上邮箱群发（info@ + sales@ + ceo@ 同时发 = 找死）
