---
name: auto-smtp-email
description: 通过 SMTP 自动发送单封业务邮件，适用于外贸开发、客户背调后的跟进、邮件模板发送等场景。支持抄送、签名文件、HTML 模板和模板变量，支持从本地 env 文件读取邮箱凭证，默认先预览后发送。对于外贸开发信，正文默认按客户背调结果全定制生成，只复用结构模板，不复用通用正文。当用户提到“自动发邮件”“发开发信”“根据客户调研结果发邮件”“用 163 邮箱发邮件”“SMTP 发信”“抄送邮件”“HTML 邮件模板”时使用。
---

# SMTP 自动发邮件

## 适用范围

- 使用 `163`、企业邮箱或其他支持 SMTP 的邮箱发送邮件
- 根据客户背调结果生成并发送首封开发信或跟进邮件
- 用户已提供收件人、主题、正文，或只提供了上游素材需要你整理成邮件

## 默认策略

1. 未明确要求立即发送时，先预览，不真实发信。
2. 凭证只从本地 env 文件读取，不写进对话或 `SKILL.md`。
3. **发信前必须先检查 `references/credentials.env`（真实凭证文件）是否存在且已填写必填项。** 若已配置，直接用于 `--dry-run` / 发送，**不要**再向用户索要 SMTP 账号或授权码，**不要**把 `credentials.env.example` 当作当前生效配置去读——`.example` 只是字段模板，用于初次复制或核对变量名。
4. 仅当 `credentials.env` 不存在、无法读取或缺少必填键时，再参考 [references/credentials.env.example](references/credentials.env.example) 的格式，并提示用户在本机补全 `references/credentials.env`（或说明沙箱内未挂载该文件）。

### DeerFlow / 斜杠无界运行时（重要）

- **`send_email.py` 会先把 `os.environ` 与 env 文件合并**；本地 **LocalSandbox** 执行 `bash` 时，子进程**继承 LangGraph 进程的环境变量**。
- 项目根目录 **`.env`** 中的 `SMTP_HOST`、`SMTP_PORT`、`SMTP_USERNAME`、`SMTP_PASSWORD`、`SMTP_FROM`、`SMTP_SECURITY`（及可选 `SMTP_FROM_NAME`）由 **`serve.sh` 在启动时 `source`** 进后端进程，**不必**依赖 Agent 用 `read_file` 去读 `credentials.env`；模型若读不到 gitignore 下的文件，仍可通过环境变量发信。
- **修改 `.env` 后请重启 `make dev`**，否则旧进程里没有新的 SMTP 变量。
- 若仍只依赖 `references/credentials.env` 文件：在 **Docker AIO 沙箱** 中需确认宿主机 `skills` 目录绑定挂载完整（含未提交文件）；更稳妥的方式仍是 **根目录 `.env`**。
5. 默认只处理单封发送；批量群发不在本 skill 范围内。
6. 当邮件属于外贸开发信时，默认生成**全定制正文**：只允许复用签名、HTML 包装和整体结构，不允许直接套用通用正文模板批量发送。

## 发送流程

### 1. 准备输入

至少确认以下字段：

- 收件人邮箱
- 邮件主题
- 邮件正文

可选字段：

- 抄送邮箱
- 密送邮箱
- 签名文件
- HTML 模板
- 模板变量

如用户只给了客户调研结果、联系人信息或开发目标，先整理出主题和正文，再进入下一步。

若邮件属于外贸开发信，额外至少整理出以下字段再写信：

- `target_company`
- `target_business_type`
- `observed_product_or_brand_signal`
- `packaging_use_case`
- `why_this_customer_matches`
- `which_product_lines_to_pitch`

如果这些信息不足，应先从背调结果里提取，而不是直接套模板写正文。

### 2. 检查凭证

1. **先读** skill 下的 `references/credentials.env`（真实配置）。已存在且含 `SMTP_PASSWORD` 等必填项即视为可用。
2. **不要**用 `credentials.env.example` 代替真实凭证；它只用于说明「需要哪些环境变量」或首次从模板复制。
3. 若需新建文件，可从 [references/credentials.env.example](references/credentials.env.example) 复制为 `credentials.env` 再填写。**该真实文件已加入 `.gitignore`，勿提交仓库。**

`send_email.py` 若未传 `--env-file`，且存在 `references/credentials.env`，会**自动读取**，无需每次在命令行里指定路径，也无需在对话里重复粘贴授权码。

也可通过 `--env-file /path/to/other.env` 指定别的 env 文件。

最少需要：

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `SMTP_SECURITY`

配置示例见 [references/credentials.env.example](references/credentials.env.example)。

### 3. 先预览

先用 `--dry-run` 检查配置和邮件内容：

```bash
# 在 skills/custom/auto-smtp-email/ 目录下执行（以便自动找到 references/credentials.env）
python3 scripts/send_email.py \
  --to "buyer@example.com" \
  --subject "Quick introduction from XXX" \
  --body-file /tmp/mail.txt \
  --dry-run
```

### 4. 确认后发送

只有在用户明确要求发送，或当前任务本身就是“直接发送”时，才执行真实发送：

```bash
python3 scripts/send_email.py \
  --to "buyer@example.com" \
  --subject "Quick introduction from XXX" \
  --body-file /tmp/mail.txt
```

## 新增能力

### 全定制开发信模式

当上游输入来自客户背调、潜客开发或官网调研时，默认进入**全定制开发信模式**。

要求：

1. 每封邮件必须明确回答“为什么联系这家公司，而不是任何一家公司”。
2. 正文至少体现 `2` 个来自客户官网或背调结果的具体信号，例如：
   - 品类：jewellery / perfume / candles / gift sets / corporate gifting
   - 场景：seasonal gifting / wedding / personalization / premium retail presentation
   - 渠道：wholesale / corporate orders / boutique / online gifting
   - 产品结构：boxes / pouches / gift bags / rigid boxes / displays
3. 必须写出 `Long Term Pack` 与对方之间最贴近的 `1-2` 个切入点，不要泛泛罗列全部产品。
4. 不允许把同一段正文换个公司名后重复发送。
5. HTML 模板只负责包装格式，**正文内容本身必须逐封重写**。

禁止做法：

- 使用“we offer many kinds of packaging for many industries”这类大而空的泛化表达作为主体内容
- 连续多封邮件只替换公司名、品类词和邮箱
- 未提及客户实际业务信号，就直接说“we noticed your company is very professional”
- 明知对方是品牌方，却写成渠道商口吻
- 明知对方是香氛礼赠品牌，却套用珠宝客户正文

### 抄送

直接传 `--cc`：

```bash
python3 scripts/send_email.py \
  --to "buyer@example.com" \
  --cc "sales-manager@example.com,owner@example.com" \
  --subject "Quick introduction from XXX" \
  --body-file /tmp/mail.txt
```

### 签名

将签名维护在独立文件，例如 `templates/signature.txt`，发送时追加：

```bash
python3 scripts/send_email.py \
  --to "buyer@example.com" \
  --subject "Quick introduction from XXX" \
  --body-file /tmp/mail.txt \
  --signature-file templates/signature.txt
```

### HTML 模板

推荐使用 `--html-template-file`，模板内支持 `{{variable}}` 占位符。

内置约定变量：

- `{{body_text}}`
- `{{signature_html}}`

也可额外传入自定义变量：

```bash
python3 scripts/send_email.py \
  --to "buyer@example.com" \
  --subject "Quick introduction from XXX" \
  --body-file /tmp/mail.txt \
  --signature-file templates/signature.txt \
  --html-template-file templates/basic.html \
  --var company_name="ACME" \
  --var sender_name="Liyang"
```

## 开发信写作规则

- 主题简短直接，不要夸张营销词
- 正文控制在 80-180 英文词，优先纯文本
- 第一段说明你是谁、为什么联系对方
- 第二段只强调 1-2 个最相关卖点
- 结尾只保留 1 个清晰 CTA
- 若上游材料信息不足，不要编造工厂规模、认证、合作案例

对外贸开发信，额外强制要求：

- 主题必须与客户当前业务场景相关，不能长期复用同一个固定标题
- 第一段必须提到客户的具体品牌、产品线、礼赠场景或包装线索
- 第二段必须说明为什么 `Long Term Pack` 的哪一类包装适合对方
- CTA 必须轻量，例如分享 catalog、分享几个 suitable styles、看是否值得进一步交流
- 如果无法从背调结果中提炼出明确切入点，应先补背调，不要硬写

## 与客户背调联动

当上游输入是客户背调结果时：

1. 提取公司名、联系人、产品方向、市场/采购线索
2. 额外提取至少 `2-4` 个可写进开发信的客户信号
3. 用这些信息重写首句、价值点和 CTA
4. 先给用户一个邮件预览
5. 用户确认后再执行发送脚本

建议的写信前检查清单：

- 我是否明确写出了对方是哪一类公司？
- 我是否引用了对方官网上真实存在的产品或礼赠场景？
- 我是否只推荐了最相关的 `1-2` 类包装产品？
- 如果把公司名替换掉，这封邮件是否还成立？
  - 如果成立，说明还不够定制，需重写。

## 实用命令

### 直接传正文

```bash
python3 scripts/send_email.py \
  --to "buyer@example.com" \
  --subject "Cooperation opportunity" \
  --body "Hello, this is a short introduction..."
```

### 发送 HTML 邮件

```bash
python3 scripts/send_email.py \
  --to "buyer@example.com" \
  --subject "Product introduction" \
  --body-file /tmp/mail.txt \
  --html-file /tmp/mail.html
```

### 使用 HTML 模板 + 签名 + 抄送

```bash
python3 scripts/send_email.py \
  --to "buyer@example.com" \
  --cc "manager@example.com" \
  --subject "Product introduction" \
  --body-file templates/mail.txt \
  --signature-file templates/signature.txt \
  --html-template-file templates/basic.html \
  --var company_name="ACME" \
  --var sender_name="aislash" \
  --dry-run
```

## 注意事项

- `163` 邮箱通常使用 SMTP 授权码，不直接使用登录密码
- 不要在对话中回显完整密码或授权码
- 如果用户未明确允许真实发送，保持在预览模式
- 若 SMTP 连接失败，先检查端口、安全模式和授权码是否正确

## 附加说明

- 详细配置见 [reference.md](reference.md)
- 发送脚本见 [scripts/send_email.py](scripts/send_email.py)
- 可参考 [templates/basic.html](templates/basic.html) 和 [templates/signature.txt](templates/signature.txt)
