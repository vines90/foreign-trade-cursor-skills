---
name: b2b-customer-research
description: 外贸客户背景调查技能。输入客户公司网站URL，自动抓取并分析客户业务信息，生成结构化客户背调报告，包含公司概况、产品/业务、目标市场、关键联系人（含邮箱、LinkedIn、WhatsApp）、采购偏好等。当用户提到"客户背调"、"外贸客户开发"、"客户调研"、"分析这个客户"、"查一下这家公司"、"帮我调查这个网站"时使用。
---

# 外贸客户背调技能

## 工具优先级（必须按这个顺序，缺一不可）

| 顺序 | 工具 | 用途 | 何时用 |
|---|---|---|---|
| 1 | `WebFetch` | 直接抓官网各页面 markdown | 默认必跑 |
| 2 | `WebSearch` | Google-style 联网搜索 | **必须跑**：补 LinkedIn / Facebook / WhatsApp / 海关、新闻、奖项 |
| 3 | `cursor-ide-browser` MCP | 浏览器渲染 | WebFetch 失败、SPA、要登录态时 |
| 4 | `firecrawl-scrape` skill | 反爬强的站点 | WebFetch+browser 都失败时 |

⚠️ **不能只跑 WebFetch**。官网通常不会主动暴露 LinkedIn 公司主页、采购总监 LinkedIn、WhatsApp Business 号、海关进口数据，这些必须靠 WebSearch 找。
之前历史报告里 `LinkedIn / WhatsApp 全是空` 就是因为只 fetch 了官网。

---

## 工作流程

### Step 1：制定抓取计划

收到客户网站URL后，确定需要抓取的页面列表：

```
必须抓取（WebFetch）：
- 首页 (/)
- 关于我们 (/about, /about-us, /company)
- 产品/服务页面 (/products, /services, /solutions)
- 联系方式 (/contact, /contact-us)

优先抓取（WebFetch）：
- 团队页面 (/team, /our-team, /people, /leadership, /management)
- 新闻/博客 (/news, /blog, /press)
- 合作伙伴/认证 (/partners, /certifications, /clients)

必须用 WebSearch 补的（官网通常没有）：
- 公司 LinkedIn 主页
- 创始人 / CEO / 采购总监 LinkedIn
- Facebook / Instagram 商业主页
- WhatsApp Business 号码
- 海关进口数据（importyeti / panjiva 公开页）
- 近期新闻 / 收购 / 融资 / 展会
```

### Step 2：抓取官网（WebFetch）

对每个目标页面调用 `WebFetch(url=...)`。
失败 → 切 `cursor-ide-browser`（`browser_navigate` + `browser_snapshot`）。
仍失败 → 切 `firecrawl-scrape` skill。

### Step 3：联网搜索（WebSearch）⭐ 必跑

按下面 6 类 query 模板各跑一次 WebSearch（替换 `{COMPANY}` 和 `{DOMAIN}`）：

```
1. LinkedIn 公司主页
   "{COMPANY}" site:linkedin.com/company
   或：{COMPANY} linkedin

2. 决策人 LinkedIn
   "{COMPANY}" (CEO OR "managing director" OR "head of purchasing" OR "procurement manager") site:linkedin.com/in

3. Facebook / Instagram
   "{COMPANY}" site:facebook.com
   "{COMPANY}" site:instagram.com

4. WhatsApp Business
   "{COMPANY}" whatsapp
   "{DOMAIN}" "+44" OR "+1" OR "+49" whatsapp

5. 海关 / 进口数据
   "{COMPANY}" importyeti
   "{COMPANY}" panjiva
   "{COMPANY}" "bill of lading"

6. 近期动态 / 采购信号
   "{COMPANY}" 2026
   "{COMPANY}" "looking for suppliers" OR "new product" OR "expansion"
   "{COMPANY}" trade show OR exhibition
```

把每个 query 找到的关键 URL 记下来，再用 `WebFetch` 进去抓详情。

### Step 4：浏览器降级方案

LinkedIn 页面常返回反爬空内容，此时：

```
browser_navigate(url="https://linkedin.com/company/xxx")
browser_snapshot()
# 不强求登录，能拿到公司简介、员工数、行业即可
```

WhatsApp 号通常在官网右下角悬浮按钮 / 联系页 footer，
WebFetch 返回的 markdown 找不到就上 `browser_take_screenshot` 看截图。

### Step 5：提取关键信息

**公司基本信息**
- 公司名称（含中英文）
- 成立年份 / 公司规模（员工数）
- 总部地址 / 工厂地址
- 公司类型（制造商/贸易商/分销商/零售商）

**业务信息**
- 主营产品/服务（列出具体品类）
- 品牌名称
- 主要目标市场（国家/地区）
- 销售渠道（线上/线下/批发/零售）
- 年营业额（如有披露）

**认证与资质**
- 质量认证（ISO、CE、UL、RoHS等）
- 行业认证/奖项

**联系人信息（重点）**
- 关键联系人姓名 + 职位
- **邮箱地址**（在网页中重点查找，常见格式：name@company.com、info@、sales@、export@）
- 电话/传真
- **LinkedIn 个人主页 URL**（必填，从 WebSearch Step 3 拿）
- **WhatsApp 号**（必填如能找到）

**社交渠道（公司层面）**
- LinkedIn 公司主页
- Facebook
- Instagram
- YouTube / TikTok（如有）

**采购偏好与合作信号**
- 最小起订量（MOQ）
- 支付方式
- 是否有代理/分销商招募信息
- 海关数据中近 12 月进口频率/金额（如有）
- 近期动态（新品、展会参与、扩张计划）

### Step 6：邮箱挖掘专项

在抓取 `/contact` 页面时，额外关注：
- 页面中明文显示的邮箱
- `mailto:` 链接
- 图片中显示的邮箱（在 snapshot 描述中寻找）
- 页脚中的联系邮箱

常见邮箱模式提取：`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`

如果官网没有找到个人邮箱，按以下顺序补：
1. WebSearch: `"{name}" "{company}" email`
2. 从 LinkedIn snapshot 拿
3. 用域名 + 命名规则推测：`first.last@domain` / `firstinitial+last@domain` / `first@domain`（推测的需在报告里标"未验证"）

### Step 7：生成背调报告

使用以下模板输出报告（保存到 `output/research/<slug>_<date>.md`）：

---

```markdown
# 客户背调报告

**目标公司**：[公司名称]
**官网**：[URL]
**调研日期**：[日期]
**报告评级**：[⭐⭐⭐⭐⭐ 高价值 / ⭐⭐⭐ 中等 / ⭐ 信息不足]
**调研来源**：官网 ✅ / WebSearch ✅ / LinkedIn ✅ / 海关数据 ⚠️

---

## 一、公司概况

| 项目 | 内容 |
|------|------|
| 公司全称 | |
| 成立年份 | |
| 公司规模 | |
| 公司类型 | 制造商 / 贸易商 / 分销商 |
| 总部地址 | |
| 主营市场 | |

## 二、产品与业务

**主营产品/服务：**
- 产品1：[描述]
- 产品2：[描述]

**品牌：** [品牌名]
**目标客户：** [B2B/B2C，行业类型]
**销售渠道：** [线上平台/线下经销商/直销]

## 三、认证与资质

- [认证名称 1]
- [认证名称 2]
- 奖项/荣誉：[如有]

## 四、社交与联系渠道（公司）⭐

| 渠道 | URL / 账号 | 来源 |
|---|---|---|
| 官网 | | WebFetch |
| LinkedIn 公司 | | WebSearch |
| Facebook | | WebSearch |
| Instagram | | WebSearch |
| WhatsApp Business | | 官网 / WebSearch |
| 公司主电话 | | 官网 |
| 通用邮箱 | sales@ / info@ / purchase@ | 官网 |

## 五、关键联系人 ⭐

| 姓名 | 职位 | 邮箱 | LinkedIn | WhatsApp | 来源 |
|------|------|------|---|---|------|
| [姓名] | [职位] | **[邮箱]** | [URL] | [+号码] | LinkedIn / 官网 |

## 六、合作潜力评估

**采购信号：**
- [ ] 有明确分销商招募信息
- [ ] 有参加国际展会
- [ ] 海关数据显示近 6 月有进口
- [ ] 近期有扩张/新品动态
- [ ] 网站有多语言支持

**建议开发策略：**
[根据调研结果给出1-2条具体建议]

## 七、信息来源

| 来源 | 状态 | 关键信息 |
|------|---------|---------|
| 官网首页 | ✅/❌ | |
| 官网 About/Contact | ✅/❌ | |
| LinkedIn 公司页 | ✅/❌ | |
| LinkedIn 决策人页 | ✅/❌ | |
| Facebook / IG | ✅/❌ | |
| WhatsApp 号 | ✅/❌ | |
| 海关数据 | ✅/❌ | |
| 近期新闻 | ✅/❌ | |

---
*本报告由 AI 自动生成，结合 WebFetch + WebSearch + LinkedIn snapshot 多源交叉，建议人工二次核验关键联系人邮箱。*
```

---

## 注意事项

- **必须跑 WebSearch**，否则报告里 LinkedIn / WhatsApp / 海关数据全部空白 = 不合格
- 若网站加载失败，报告中注明具体原因（反爬、需登录等）
- 邮箱信息即使只有通用邮箱（如 info@），也必须列出
- 推测的邮箱必须标"未验证"
- 报告语言：中文为主，公司名/产品名/URL 保留原文
- LinkedIn URL 必须用 `linkedin.com/company/` 或 `linkedin.com/in/` 完整路径
- WhatsApp 号统一 E.164 格式（带 `+` 国家码）
