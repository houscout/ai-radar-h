"""Run the authorized weekly research and publish validated snapshots."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from validate_snapshot import validate_snapshot

TASK_ROOT = Path.home() / ".codex" / "radar-weekly"
SKILL_ROOT = Path(__file__).resolve().parents[1]
PROJECTS = [
    ("ai", "houscout/ai-radar-h"),
    ("biomedicine", "houscout/-biomedic-radar-"),
]


def command(args, cwd=None, timeout=120):
    result = subprocess.run(
        [str(arg) for arg in args], cwd=cwd, capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=timeout,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"},
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    if result.returncode:
        raise RuntimeError(f"{Path(str(args[0])).name} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def run(check_only=False):
    config = json.loads((TASK_ROOT / "runtime.json").read_text(encoding="utf-8"))
    git = Path(config["git"])
    codex = Path(config["codex"])
    if not git.is_file() or not codex.is_file():
        raise RuntimeError("Git or Codex executable is missing")
    command([codex, "login", "status"], timeout=60)
    for _, repo in PROJECTS:
        command([git, "ls-remote", f"https://github.com/{repo}.git", "HEAD"], timeout=60)
    now = datetime.now(timezone.utc)
    local = now.astimezone(ZoneInfo("America/Matamoros"))
    date = local.date().isoformat()
    if check_only:
        return {"status": "preflight-passed", "date": date, "projects": [p[1] for p in PROJECTS]}
    checkouts = TASK_ROOT / "checkouts"
    checkouts.mkdir(parents=True, exist_ok=True)
    active = []
    results = []
    path = f"data/daily/{date}.json"
    for domain, repo in PROJECTS:
        checkout = checkouts / domain
        if not checkout.exists():
            command([git, "clone", f"https://github.com/{repo}.git", checkout], timeout=180)
        if command([git, "-C", checkout, "remote", "get-url", "origin"]) != f"https://github.com/{repo}.git":
            raise RuntimeError(f"Unexpected remote in {checkout}")
        if command([git, "-C", checkout, "status", "--porcelain"]):
            raise RuntimeError(f"Uncommitted files in automation checkout: {checkout}")
        command([git, "-C", checkout, "pull", "--ff-only"], timeout=180)
        if command([git, "-C", checkout, "rev-list", "--count", "origin/main..HEAD"]) != "0":
            raise RuntimeError(f"Unpublished commits in {checkout}; review the previous run")
        if (checkout / path).exists():
            results.append({"repo": repo, "status": "already-saved", "path": path})
        else:
            active.append((repo, checkout))
    if not active:
        return {"status": "already-saved", "projects": results}
    targets = "\n".join(f"- {repo}: {checkout}" for repo, checkout in active)
    prompt = (
        "Use $update-weekly-radars from " + str(SKILL_ROOT / "SKILL.md") +
        ". This is the authorized Friday weekly run. Read each target's AGENTS.md and contract. "
        "Search live web news from the preceding seven days; open sources and select up to five "
        "distinct verified signals per target. Exclude other repositories. Targets:\n" + targets +
        "\nWrite only " + path + " in each target. Set snapshotDate to " + date +
        " and savedAt/accessedAt to real UTC times. Use the existing daily schema, declaring "
        "the weekly window in collection.scope. Do not overwrite existing snapshots. "
        "Do not run Git mutations, publish files, alter guides/contracts or create other files. "
        "The wrapper validates and publishes afterward. If no verified signals exist, leave "
        "that target without a file and report why. Return a concise Spanish summary with "
        "source links, missing signals, and limitations."
    )
    TASK_ROOT.joinpath("logs").mkdir(exist_ok=True)
    log_path = TASK_ROOT / "logs" / f"{date}-codex.log"
    summary_path = TASK_ROOT / "logs" / f"{date}-summary.md"
    with log_path.open("a", encoding="utf-8") as log:
        process = subprocess.run(
            [str(codex), "--no-daemon", "--search", "-a", "never", "exec",
             "--sandbox", "workspace-write",
             "-c", "sandbox_workspace_write.network_access=true",
             "--skip-git-repo-check", "-C", str(checkouts),
             "--add-dir", str(TASK_ROOT / "logs"),
             "--color", "never", "-o", str(summary_path), "-"],
            input=prompt, text=True, encoding="utf-8", stdout=log, stderr=log,
            timeout=2700,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    if process.returncode:
        raise RuntimeError(f"Codex run failed; inspect {log_path}")
    approved = []
    for repo, checkout in active:
        changes = command([git, "-C", checkout, "status", "--porcelain", "--untracked-files=all"])
        if any(line[3:] != path for line in changes.splitlines()):
            raise RuntimeError(f"Unexpected modified path in {repo}; publication stopped")
        target = checkout / path
        if not target.exists():
            results.append({"repo": repo, "status": "no-snapshot-produced"})
            continue
        snapshot = json.loads(target.read_text(encoding="utf-8-sig"))
        schema = json.loads((checkout / "contracts/daily-signals.schema.json").read_text(encoding="utf-8"))
        if snapshot["snapshotDate"] != date:
            raise ValueError("Wrong scheduled snapshot date")
        count = validate_snapshot(snapshot, schema, weekly=True)
        approved.append((repo, checkout, target, count))
    # Validate all produced files before the first publication.
    for repo, checkout, target, count in approved:
        command([git, "-C", checkout, "add", "--", path])
        command([git, "-C", checkout, "commit", "-m", f"data: guardar señales semanales del {date}"])
        try:
            command([git, "-C", checkout, "push", "origin", "HEAD:main"], timeout=180)
            command([git, "-C", checkout, "fetch", "origin", "main"], timeout=180)
            remote = command([git, "-C", checkout, "show", f"origin/main:{path}"])
            if json.loads(remote) != json.loads(target.read_text(encoding="utf-8-sig")):
                raise RuntimeError("Remote content differs")
            results.append({"repo": repo, "status": "published", "signals": count,
                            "url": f"https://github.com/{repo}/blob/main/{path}"})
        except Exception as exc:
            results.append({"repo": repo, "status": "publication-failed", "error": str(exc)})
    success = all(item["status"] in ("published", "already-saved") for item in results)
    return {"status": "completed" if success else "partial", "projects": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    TASK_ROOT.mkdir(parents=True, exist_ok=True)
    lock = TASK_ROOT / "run.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise RuntimeError("Another run is active, or a stale run.lock requires review")
    os.close(descriptor)
    try:
        try:
            result = run(args.check)
        except Exception as exc:
            result = {"status": "failed", "error": str(exc)}
        output = json.dumps(result, ensure_ascii=False, indent=2)
        (TASK_ROOT / "last-run.json").write_text(output + "\n", encoding="utf-8")
        if sys.stdout:
            print(output)
        if result["status"] in ("failed", "partial"):
            raise SystemExit(1)
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

