#!/usr/bin/env python3
"""
workspace-init: 幂等初始化外贸项目工作空间。

用法:
    python3 .cursor/skills/workspace-init/scripts/init.py [--check-only] [--verbose]

--check-only  只体检，不创建/修改任何文件
--verbose     输出每个动作（默认只在变化或异常时输出）
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

# 本脚本位于 PROJECT_ROOT/.cursor/skills/workspace-init/scripts/init.py
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent  # 跳出 .cursor/skills/<skill>/

REQUIRED_DIRS = [
    "output/leads",
    "output/raw",
    "output/research",
    "output/emails/drafts",
    "output/emails/sent",
    "output/logs",
    ".cursor/state",
    ".cursor/cache/apify",
    ".cursor/cache/i18n",
]

# 在每个目录下放一个 .gitkeep，方便空目录被 git 跟踪（但 raw/logs/state/cache 本身被 gitignore，无需）
KEEP_DIRS = [
    "output/leads",
    "output/research",
    "output/emails/drafts",
    "output/emails/sent",
]

GITIGNORE_REQUIRED = SKILL_DIR / "references" / "gitignore-required.txt"

SMTP_CRED_PATH = (
    PROJECT_ROOT / ".cursor" / "skills" / "auto-smtp-email" / "references" / "credentials.env"
)
SMTP_CRED_EXAMPLE = (
    PROJECT_ROOT
    / ".cursor"
    / "skills"
    / "auto-smtp-email"
    / "references"
    / "credentials.env.example"
)
SMTP_REQUIRED_KEYS = ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM"]

ENV_PATH = PROJECT_ROOT / ".env"
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"
BITABLE_STATE_PATH = PROJECT_ROOT / ".cursor" / "state" / "bitable.json"


class CheckResult(NamedTuple):
    name: str
    status: str  # OK | WARN | FAIL
    detail: str


# ---------- 通用 ----------


def log(verbose: bool, msg: str) -> None:
    if verbose:
        print(msg)


def parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


# ---------- Step 1: directories ----------


def ensure_dirs(check_only: bool, verbose: bool) -> CheckResult:
    created: list[str] = []
    for rel in REQUIRED_DIRS:
        d = PROJECT_ROOT / rel
        if not d.exists():
            if check_only:
                created.append(rel)
            else:
                d.mkdir(parents=True, exist_ok=True)
                created.append(rel)
                log(verbose, f"  + mkdir {rel}")

    if not check_only:
        for rel in KEEP_DIRS:
            keep = PROJECT_ROOT / rel / ".gitkeep"
            if not keep.exists():
                keep.touch()
                log(verbose, f"  + touch {rel}/.gitkeep")

    if check_only and created:
        return CheckResult(
            "directory tree",
            "WARN",
            f"missing {len(created)} dirs (use without --check-only to create)",
        )
    if created:
        return CheckResult("directory tree", "OK", f"created {len(created)} new dirs")
    return CheckResult("directory tree", "OK", "all required dirs exist")


# ---------- Step 2: .gitignore ----------


def ensure_gitignore(check_only: bool, verbose: bool) -> CheckResult:
    required: list[str] = []
    for raw in GITIGNORE_REQUIRED.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        required.append(s)

    if not GITIGNORE_PATH.exists():
        if check_only:
            return CheckResult(".gitignore", "WARN", f"missing file ({len(required)} entries needed)")
        GITIGNORE_PATH.write_text("# auto-generated header by workspace-init\n", encoding="utf-8")
        log(verbose, "  + created empty .gitignore")

    existing = {
        line.strip()
        for line in GITIGNORE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    missing = [item for item in required if item not in existing]

    if not missing:
        return CheckResult(".gitignore", "OK", "all required entries present")

    if check_only:
        return CheckResult(".gitignore", "WARN", f"missing {len(missing)} entries: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}")

    with GITIGNORE_PATH.open("a", encoding="utf-8") as f:
        f.write("\n# ---- workspace-init: required entries ----\n")
        for item in missing:
            f.write(f"{item}\n")
            log(verbose, f"  + .gitignore += {item}")
    return CheckResult(".gitignore", "OK", f"appended {len(missing)} entries")


# ---------- Step 3: credentials ----------


def check_apify_env() -> CheckResult:
    if not ENV_PATH.exists():
        return CheckResult(".env (APIFY_TOKEN)", "FAIL", f"{ENV_PATH.name} not found — create it with APIFY_TOKEN=...")
    env = parse_env_file(ENV_PATH)
    token = env.get("APIFY_TOKEN", "").strip()
    if not token:
        return CheckResult(".env (APIFY_TOKEN)", "FAIL", "APIFY_TOKEN missing — required by apify-ultimate-scraper")
    if not token.startswith("apify_api_"):
        return CheckResult(".env (APIFY_TOKEN)", "WARN", "APIFY_TOKEN format looks unusual (expected apify_api_...)")
    return CheckResult(".env (APIFY_TOKEN)", "OK", f"token loaded ({len(token)} chars)")


def check_smtp_credentials(check_only: bool, verbose: bool) -> CheckResult:
    if not SMTP_CRED_PATH.exists():
        if check_only:
            return CheckResult(
                "smtp credentials",
                "FAIL",
                f"missing {SMTP_CRED_PATH.relative_to(PROJECT_ROOT)} (copy from credentials.env.example and fill in)",
            )
        if SMTP_CRED_EXAMPLE.exists():
            shutil.copy(SMTP_CRED_EXAMPLE, SMTP_CRED_PATH)
            log(verbose, f"  + copied {SMTP_CRED_EXAMPLE.name} -> credentials.env (placeholder)")
            return CheckResult(
                "smtp credentials",
                "WARN",
                "placeholder created from .example — fill in real SMTP host/user/password before sending",
            )
        return CheckResult("smtp credentials", "FAIL", "credentials.env.example also missing — cannot create placeholder")

    cfg = parse_env_file(SMTP_CRED_PATH)
    missing = [k for k in SMTP_REQUIRED_KEYS if not cfg.get(k, "").strip()]
    if missing:
        return CheckResult("smtp credentials", "FAIL", f"missing keys: {', '.join(missing)}")

    placeholders = [k for k in SMTP_REQUIRED_KEYS if "your_" in cfg[k].lower() or cfg[k].endswith("@example.com")]
    if placeholders:
        return CheckResult("smtp credentials", "WARN", f"placeholder values still in: {', '.join(placeholders)}")

    return CheckResult(
        "smtp credentials",
        "OK",
        f"sender = {cfg.get('SMTP_FROM_NAME', '')} <{cfg['SMTP_FROM']}> via {cfg['SMTP_HOST']}:{cfg['SMTP_PORT']}",
    )


def check_bitable_state() -> CheckResult:
    if not BITABLE_STATE_PATH.exists():
        return CheckResult(
            "bitable state",
            "WARN",
            "not initialized — run bitable-trade-customer setup before storing customers",
        )
    try:
        import json

        data = json.loads(BITABLE_STATE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return CheckResult("bitable state", "FAIL", f"cannot parse: {e}")
    if not data.get("app_token"):
        return CheckResult("bitable state", "FAIL", "app_token empty — re-run bitable-trade-customer setup")
    return CheckResult("bitable state", "OK", f"app_token = {data['app_token'][:8]}... ({len(data.get('tables', {}))} tables)")


# ---------- Step 4: runtime ----------


def _run_version(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=False)
        text = (out.stdout or out.stderr).strip().splitlines()
        return text[0] if text else None
    except Exception:
        return None


def check_python() -> CheckResult:
    v = sys.version_info
    if v < (3, 10):
        return CheckResult("python3", "WARN", f"current {v.major}.{v.minor}.{v.micro} < 3.10 (some skills may break)")
    return CheckResult("python3", "OK", f"{v.major}.{v.minor}.{v.micro}")


def check_node() -> CheckResult:
    raw = _run_version(["node", "--version"])
    if not raw:
        return CheckResult("node", "WARN", "node not found — apify-ultimate-scraper scripts need it")
    ver = raw.lstrip("v")
    try:
        major = int(ver.split(".")[0])
        if major < 18:
            return CheckResult("node", "WARN", f"current {raw} < v18 (apify SDK requires 18+)")
    except ValueError:
        pass
    return CheckResult("node", "OK", raw)


# ---------- main ----------


def print_status(results: list[CheckResult]) -> int:
    print("\n=== Workspace Status ===")
    width = max(len(r.name) for r in results) + 2
    for r in results:
        tag = f"[{r.status:<4}]"
        print(f"{tag} {r.name.ljust(width)}{r.detail}")

    fail_count = sum(1 for r in results if r.status == "FAIL")
    warn_count = sum(1 for r in results if r.status == "WARN")

    print("\n=== Next steps ===")
    if fail_count:
        print(f"- {fail_count} FAIL item(s) above must be fixed before running other skills")
    next_steps = []
    if any(r.name == "bitable state" and r.status == "WARN" for r in results):
        next_steps.append("- 入库前：调用 bitable-trade-customer skill 完成首次 setup")
    if any(r.name == "smtp credentials" and r.status == "WARN" for r in results):
        next_steps.append("- 发邮件前：编辑 .cursor/skills/auto-smtp-email/references/credentials.env 填入真实凭证")
    if any(r.name == ".env (APIFY_TOKEN)" and r.status == "FAIL" for r in results):
        next_steps.append("- 拓客前：在 .env 写入 APIFY_TOKEN")
    if not next_steps and fail_count == 0:
        next_steps.append("- 全部就绪，可直接调用 trade-customer-search / auto-trade-customer-development")
    print("\n".join(next_steps))

    return 0 if fail_count == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="只体检，不创建任何文件")
    parser.add_argument("--verbose", action="store_true", help="输出每个动作")
    args = parser.parse_args()

    print(f"workspace-init :: project root = {PROJECT_ROOT}")
    if args.check_only:
        print("mode: CHECK ONLY (no files will be created/modified)")
    else:
        print("mode: APPLY (idempotent: existing dirs/files untouched)")

    results: list[CheckResult] = []
    results.append(ensure_dirs(args.check_only, args.verbose))
    results.append(ensure_gitignore(args.check_only, args.verbose))
    results.append(check_apify_env())
    results.append(check_smtp_credentials(args.check_only, args.verbose))
    results.append(check_bitable_state())
    results.append(check_python())
    results.append(check_node())

    return print_status(results)


if __name__ == "__main__":
    raise SystemExit(main())
