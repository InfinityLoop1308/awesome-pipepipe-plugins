"""Decide what a pull request changes and whether it can be checked automatically.

Usage: plan.py <base index.json> <head index.json> <changed files list> <report.md>
Writes `entries=<json list>` and `manual=true|false` to $GITHUB_OUTPUT.
Exit 1 when the PR is invalid. New plugins and source changes are built and checked
too, but `manual=true` keeps them from being merged automatically.
"""
import json
import os
import pathlib
import re
import sys

ALLOWED_FILES = {"index.json", "README.md"}
SOURCE_RE = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ID_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = ("pluginId", "name", "versionCode", "versionName", "apiVersion", "author",
            "package", "sha256", "signature", "publicKey", "source")


def by_id(path):
    plugins = json.loads(pathlib.Path(path).read_text())["plugins"]
    result = {}
    for p in plugins:
        if p.get("pluginId") in result:
            raise ValueError(f"duplicate pluginId {p.get('pluginId')}")
        result[p.get("pluginId")] = p
    return result


def check_entry(entry, old, problems, manual):
    pid = entry.get("pluginId")
    missing = [f for f in REQUIRED if f not in entry]
    if missing:
        problems.append(f"`{pid}`: missing fields {', '.join(missing)}")
        return False
    if not isinstance(pid, str) or not ID_RE.match(pid) or len(pid) > 128:
        problems.append(f"`{pid}`: invalid pluginId")
    if not SOURCE_RE.match(str(entry["source"])):
        problems.append(f"`{pid}`: source must be https://github.com/<owner>/<repo>")
    if not SHA_RE.match(str(entry["sha256"]).lower()):
        problems.append(f"`{pid}`: sha256 is not 64 hex characters")
    if not isinstance(entry["versionCode"], int):
        problems.append(f"`{pid}`: versionCode is not an integer")
    if old is None:
        manual.append(f"`{pid}`: new plugin, first listing is reviewed by a maintainer")
    elif old.get("source") != entry["source"]:
        manual.append(f"`{pid}`: source changed from `{old.get('source')}`")
    if isinstance(entry["versionCode"], int) and old is not None:
        if old.get("publicKey") != entry["publicKey"]:
            manual.append(f"`{pid}`: publicKey changed")
        if entry["versionCode"] < old.get("versionCode", 0):
            problems.append(f"`{pid}`: versionCode decreased")
        elif entry["versionCode"] == old.get("versionCode"):
            manual.append(f"`{pid}`: entry changed without a new version")
    return True


def main():
    base_path, head_path, files_path, report_path = sys.argv[1:5]
    problems, manual = [], []
    changed_files = pathlib.Path(files_path).read_text().split()
    extra = sorted(set(changed_files) - ALLOWED_FILES)
    if extra:
        problems.append("PR changes files other than index.json/README.md: "
                        + ", ".join(f"`{f}`" for f in extra))
    entries = []
    try:
        base_doc = json.loads(pathlib.Path(base_path).read_text())
        head_doc = json.loads(pathlib.Path(head_path).read_text())
        changed_keys = sorted(k for k in set(base_doc) | set(head_doc)
                              if k != "plugins" and base_doc.get(k) != head_doc.get(k))
        if changed_keys:
            manual.append("index fields changed: " + ", ".join(f"`{k}`" for k in changed_keys))
        base, head = by_id(base_path), by_id(head_path)
        removed = sorted(set(base) - set(head))
        if removed:
            manual.append("PR removes plugins: " + ", ".join(f"`{r}`" for r in removed))
        for pid, entry in head.items():
            old = base.get(pid)
            if entry == old:
                continue
            if check_entry(entry, old, problems, manual):
                entries.append(entry)
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        problems.append(f"index.json is invalid: {e}")
    if not entries and not problems and not manual:
        problems.append("PR does not change any plugin entry")

    lines = ["### Plan", ""]
    lines += [f"- check `{e['pluginId']}` {e['versionName']} ({e['versionCode']})"
              for e in entries]
    if problems:
        lines += ["", "**Invalid:**"] + [f"- {p}" for p in problems]
    if manual:
        lines += ["", "**Needs a maintainer:**"] + [f"- {m}" for m in manual]
    pathlib.Path(report_path).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as out:
        out.write("entries=" + json.dumps([] if problems else entries) + "\n")
        out.write(f"manual={'true' if manual else 'false'}\n")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
