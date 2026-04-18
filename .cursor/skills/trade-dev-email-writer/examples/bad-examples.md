# 反面示例

> 这些是**绝对不要写**的开发信。每个都标注了"为什么这是垃圾"。

---

## 反例 1：通用万能体（最常见的坏邮件）

```
Subject: Best Quality Packaging Boxes from China

Dear Sir/Madam,

Hope this email finds you well.

My name is Yang Li and I am writing to you from Long Term Pack Limited,
a leading manufacturer of jewellery packaging in China with 20+ years of
experience. We supply premium quality boxes to many famous brands worldwide.

We can offer you the best price and the highest quality. Our products
include velvet boxes, paper boxes, leather boxes, wooden boxes, plastic
boxes, gift bags, pouches, displays, and many more.

Please feel free to contact us for more information. We can satisfy any
of your packaging needs.

Looking forward to your reply!

Best regards,
Yang
Long Term Pack Limited
```

**问题诊断**：

- ❌ `Dear Sir/Madam` — 群发标志
- ❌ `Hope this email finds you well` — 烂大街开场
- ❌ `leading manufacturer` / `premium quality` / `best price` / `highest quality` — 全是营销自夸
- ❌ 第三段罗列了 9 种产品，等于没推荐任何一种
- ❌ `We can satisfy any of your packaging needs` — 大而空
- ❌ `Looking forward to your reply!` — 标准尾巴 + `!`
- ❌ **替换法测试**：把"Long Term Pack Limited"换成任何一家中国包装厂，邮件依旧成立 → 这是模板，不是开发信
- ❌ 主题 `Best Quality Packaging Boxes from China` — 含 `Best`，泛化，且没有"为什么联系你"

**反垃圾邮件检查**：❌ 多个高频垃圾词、群发开头、与正文无关的主题

---

## 反例 2：硬卖体（最容易进垃圾箱的写法）

```
Subject: 🔥🔥 LIMITED TIME!! 50% OFF on Premium Jewellery Boxes!!! 🔥🔥

Dear Friend,

CONGRATULATIONS! You have been selected for our exclusive offer!

🎁 100% FREE samples for first 10 customers!!!
💰 Save up to $5,000 on your next bulk order!!!
⏰ ACT NOW — offer expires in 48 hours!!!

CLICK HERE to claim your discount: http://bit.ly/3xYz9a

We are the BEST and CHEAPEST packaging supplier in China!!!
100% money-back guarantee!!! No risk!!!

BUY NOW or regret forever!

🌟 Visit www.ltspack.com 🌟
📧 contact@ltspack.com 📧
📞 WhatsApp: +86 138-xxxx-xxxx 📞

Sent from my marketing automation
```

**问题诊断**：每一行都是问题。这是"教科书级垃圾邮件"。

- ❌ 主题：emoji × 4、`!!` × 4、全大写、`50% OFF`、`$`、`LIMITED TIME` — 6 项垃圾邮件特征同时命中
- ❌ `Dear Friend` — 100% 群发
- ❌ `CONGRATULATIONS! You have been selected` — 标准营销诈骗模板
- ❌ `100% FREE`、`Save up to $5,000`、`ACT NOW`、`offer expires`、`CLICK HERE`、`BEST`、`CHEAPEST`、`BUY NOW`、`100% money-back guarantee`、`No risk` — 至少 10 个高频垃圾词
- ❌ `http://bit.ly/...` 短链 — 反垃圾邮件直接拦
- ❌ 4 个 emoji + 多个 `!!!` 在签名里 — 域名声誉直接被毁
- ❌ `Sent from my marketing automation` — 自动化标签，邮件服务商一眼识别

**结果**：**100% 进垃圾箱**，且发信域名声誉受损，影响后续所有邮件。

---

## 反例 3：换名群发（看似定制实则模板）

发给 Arya：

```
Subject: Cooperation Opportunity with Arya

Dear Arya Team,

We are Long Term Pack, a professional jewellery packaging manufacturer
in China. We saw your website and noticed you are in the jewellery
business. We would like to cooperate with you.

We can provide you with high quality packaging at competitive prices.
Please find our catalog attached.

Looking forward to your reply.

Best regards,
Yang
```

发给 TH Findings：

```
Subject: Cooperation Opportunity with TH Findings

Dear TH Findings Team,

We are Long Term Pack, a professional jewellery packaging manufacturer
in China. We saw your website and noticed you are in the jewellery
business. We would like to cooperate with you.

We can provide you with high quality packaging at competitive prices.
Please find our catalog attached.

Looking forward to your reply.

Best regards,
Yang
```

发给 Cooksongold：

```
Subject: Cooperation Opportunity with Cooksongold

Dear Cooksongold Team,

We are Long Term Pack, a professional jewellery packaging manufacturer
in China. We saw your website and noticed you are in the jewellery
business. We would like to cooperate with you.

...（一模一样）
```

**问题诊断**：

- ❌ **替换法测试 100% 失败**：除了公司名，三封信完全一样
- ❌ `We saw your website and noticed you are in the jewellery business` — 等于没说，所有珠宝相关公司都适用
- ❌ `We would like to cooperate with you` — 没说怎么合作
- ❌ `high quality packaging at competitive prices` — 任何包装厂都能说这句
- ❌ 首封就附 catalog — 反垃圾邮件减分
- ❌ 三封信连续从同一域名发出，且内容相似度 > 90% — Gmail 直接判定为批量营销

**正确做法**：参考 [good-examples.md](good-examples.md) 中三封信的对比 — 同一发件人、同一发件日，三封内容完全不同，每封都贴着收件人独有的信号。

---

## 反例 4：自我中心型（只说自己，不说对方）

```
Subject: Introducing Long Term Pack — Your Best Jewellery Packaging Partner

Dear Purchasing Manager,

Long Term Pack was founded in 2005 in Dongguan, China. We are a
leading manufacturer of jewellery packaging with over 20 years of
experience. Our factory covers 8,000 square meters with more than
200 employees. We have ISO9001, BSCI, and SEDEX certifications.

Our products include:
- Velvet boxes (ring, necklace, bracelet, watch)
- Paper boxes (rigid, foldable, magnetic)
- Wooden boxes (premium, antique, modern)
- Pouches and bags
- Acrylic displays
- Custom POSM
- Gift wrapping accessories

We have served clients in over 30 countries including USA, UK, Germany,
France, Japan, Australia, UAE, Saudi Arabia, Brazil, and more.

If you are interested in our products, please visit our website at
www.ltspack.com or contact us anytime.

We look forward to building a long-term partnership with your company.

Best regards,
Yang Li
Overseas Sales Manager
Long Term Pack Limited
```

**问题诊断**：

- ❌ 200 词里 **0 个** 关于收件人公司的具体信息 — 收件人感觉不到这是给他写的
- ❌ 连续罗列 7 类产品 + 10 个国家 — 信息量爆炸但无重点
- ❌ `Your Best Jewellery Packaging Partner` — 自封头衔
- ❌ `If you are interested` / `please contact us anytime` — 把 CTA 完全推给对方
- ❌ `Dear Purchasing Manager` — 没找到具体人就用通用职位称呼，也是群发标志

**正确做法**：把这 200 词砍一半，前 50 词全部用来说"对方公司有什么，我注意到了什么"，再拿剩下的 100 词说我方对应的 1–2 个能力。

---

## 反例 5：装熟体（错误的"个性化"尝试）

```
Subject: Hey buddy, long time no see!

Hi John (or whoever reads this),

I hope you and your family are doing great! I was thinking about you
the other day and remembered that we should connect about packaging.

How are things at <Company>? I bet business is booming!

I have an amazing opportunity for you that I think you'll love. Let me
know when you have 30 minutes for a call this week. I'll show you
something that will blow your mind!

Cheers,
Yang
```

**问题诊断**：

- ❌ `Hey buddy` — 不认识对方还装熟
- ❌ `Hi John (or whoever reads this)` — 占位符没删干净（真的有人这么发出去过）
- ❌ `I was thinking about you the other day` — 谎言，一眼识破
- ❌ `I bet business is booming` — 没有事实依据
- ❌ `amazing opportunity` / `blow your mind` — 营销诈骗气质
- ❌ 30 分钟通话 CTA 太重，首封不合适

---

## 共性教训

所有反面示例都犯了下面至少一项：

1. **不知道收件人是谁** → 写出来的全是放之四海皆准的废话
2. **不知道为什么联系收件人** → 第一段就垮
3. **想在一封信里说服对方下单** → 用力过猛 → 营销腔 → 进垃圾箱
4. **混淆"个性化"和"装熟"** → 假亲密 → 反感
5. **把所有产品全部塞进去** → 信息过载 → 没重点 → 没行动

**好开发信和坏开发信的根本区别**：

- 好的：**像一封私信**
- 坏的：**像一张传单**

写之前问自己：如果把这封信打印出来贴在公司公告栏，所有人都能领走，那就是传单，不是私信。
