"""Verify that the published package of an index entry matches the entry.

Usage: verify.py <entry.json> <report.md>
Exit 0: all checks passed. Exit 1: needs human review (reasons in the report).
"""
import base64
import hashlib
import json
import pathlib
import sys
import tempfile
import urllib.request
import zipfile

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

MANIFEST_FIELDS = ("pluginId", "name", "versionCode", "versionName", "apiVersion", "author")
MAX_PACKAGE = 20 * 1024 * 1024


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def download(url, dest):
    if not url.startswith("https://"):
        raise ValueError("package url is not https")
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = resp.read(MAX_PACKAGE + 1)
    if len(data) > MAX_PACKAGE:
        raise ValueError("package is larger than 20 MiB")
    pathlib.Path(dest).write_bytes(data)


def check_signature(entry):
    try:
        key = Ed25519PublicKey.from_public_bytes(base64.b64decode(entry["publicKey"]))
        key.verify(base64.b64decode(entry["signature"]), bytes.fromhex(entry["sha256"]))
        return True
    except (InvalidSignature, ValueError):
        return False


def check_manifest(path, entry, problems):
    with zipfile.ZipFile(path) as zf:
        manifest = json.loads(zf.read("plugin.json"))
    for field in MANIFEST_FIELDS:
        if manifest.get(field) != entry.get(field):
            problems.append(f"plugin.json `{field}` is `{manifest.get(field)}`, "
                            f"index has `{entry.get(field)}`")


def main():
    entry_path, report_path = sys.argv[1:3]
    entry = json.loads(pathlib.Path(entry_path).read_text())
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        published = pathlib.Path(tmp, "published.ppp")
        try:
            download(entry["package"], published)
            if sha256(published) != entry["sha256"].lower():
                problems.append("published package does not match the index sha256")
            else:
                check_manifest(published, entry, problems)
        except Exception as e:  # noqa: BLE001 - any failure means review
            problems.append(f"cannot check published package: {e}")
    if not check_signature(entry):
        problems.append("signature does not verify against publicKey")

    lines = [f"### {entry['pluginId']} {entry['versionName']} ({entry['versionCode']})", ""]
    lines.append("**Package check: passed**" if not problems else "**Result: failed**")
    lines += [f"- {p}" for p in problems]
    pathlib.Path(report_path).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
