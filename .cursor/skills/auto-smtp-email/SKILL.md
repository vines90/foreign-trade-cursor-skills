---
name: auto-smtp-email
description: 通过 SMTP 发送单封业务邮件的"发送通道"。支持抄送、签名文件、HTML 模板和模板变量，支持从本地 env 文件读取邮箱凭证，默认先预览后发送。本 skill 只负责"把准备好的草稿真实发出去"；外贸开发信的正文撰写、定制策略、反垃圾邮件检查交给 `trade-dev-email-writer`。当用户提到"用 163 邮箱发邮件"、"SMTP 发信"、"抄送邮件"、"HTML 邮件模板"、"把这封草稿发出去"时使用。
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
6. 收到的"邮件正文"如果是外贸开发信，**正文撰写、定制度、反营销腔与反垃圾邮件检查**统一由 [trade-dev-email-writer](../trade-dev-email-writer/SKILL.md) 负责，本 skill 不再重复定义那套规则；如果传入的是未经定制的通用模板正文，应先回退到 `trade-dev-email-writer` 重写，再调用本 skill 发送。

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

如用户只给了客户调研结果、联系人信息或开发目标，**不要在本 skill 里直接拼正文**——先调用 [trade-dev-email-writer](../trade-dev-email-writer/SKILL.md) 生成 `output/emails/drafts/<slug>.txt` 草稿文件，再回到本 skill 用 `--body-file` 发送。

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

> 外贸开发信的"全定制正文 / 反营销腔 / 反垃圾邮件检查"已迁移到独立 skill，详见 [trade-dev-email-writer](../trade-dev-email-writer/SKILL.md)。本节只保留发送通道侧的能力（抄送、签名、HTML 模板）。

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

> 写信本身的所有规则（结构、定制度、语气、反营销词、反垃圾邮件检查、自检清单、与客户背调的联动）统一见 [trade-dev-email-writer](../trade-dev-email-writer/SKILL.md)，本 skill 不再重复。

本 skill 在发送阶段只做最薄的一层"发送侧自检"：

- 收件人邮箱格式合法
- 主题非空
- 正文非空
- 凭证可用、SMTP 连通
- 用户已明确同意发送（否则保持 `--dry-run`）

如果传入的草稿明显是"通用模板群发"（例如 `Dear Sir/Madam` 开头、罗列全部产品线、出现 `Best price` / `Click here` 等垃圾邮件触发词），应先回退到 `trade-dev-email-writer` 重写，再调用本 skill 发送。

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
