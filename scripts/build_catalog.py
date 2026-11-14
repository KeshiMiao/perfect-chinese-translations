#!/usr/bin/env python3
"""扫描 .po 生成 catalog.json。

只依赖标准库；在仓库根目录或任意目录调用都可以。
entries 没变化时不改动文件，避免 CI 每次提交只改 generated_at。
"""

import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"
SCHEMA_VERSION = 1
MAX_BYTES = 512 * 1024
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
HEADER_PATTERN = re.compile(r"^#\s*([a-z_]+)\s*:\s*(.+)$")
DIRECTORIES = {"locale": "addon", "blender": "blender"}
REQUIRED = ("id", "name", "translation_version")


def read_header(path):
    meta = {}
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line and not line.startswith("#"):
                break
            match = HEADER_PATTERN.match(line)
            if match:
                meta[match.group(1)] = match.group(2).strip()
    return meta


def git_date(path):
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        return result.stdout.strip()
    except OSError:
        return ""


def entry_for(path):
    meta = read_header(path)
    missing = [key for key in REQUIRED if not meta.get(key)]
    if missing:
        raise ValueError("%s 缺少文件头字段：%s" % (path.relative_to(ROOT), ", ".join(missing)))

    entry_id = meta["id"]
    if not ID_PATTERN.match(entry_id):
        raise ValueError("%s 的 id 不合法：%r" % (path, entry_id))
    if path.stem != entry_id:
        raise ValueError("%s 的文件名必须与 id 一致：%s" % (path.relative_to(ROOT), entry_id))

    locale = meta.get("locale", "zh_HANS")
    if locale != "zh_HANS":
        raise ValueError("%s 的 locale 必须是 zh_HANS" % path.relative_to(ROOT))

    kind = meta.get("kind") or DIRECTORIES.get(path.parent.name, "addon")
    supported = meta.get("supported_versions", "*")
    if kind == "blender" and supported == "*":
        raise ValueError("%s 是补缺包，必须写 supported_versions" % path.relative_to(ROOT))

    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError("%s 超过 %d 字节" % (path.relative_to(ROOT), MAX_BYTES))

    return {
        "id": entry_id,
        "kind": kind,
        "module": meta.get("module", ""),
        "name": meta["name"],
        "name_zh": meta.get("name_zh", ""),
        "translator": meta.get("translator", ""),
        "category": meta.get("category", ""),
        "locale": locale,
        "translation_version": meta["translation_version"],
        "supported_versions": supported,
        "url": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "updated_at": meta.get("updated_at") or git_date(path),
    }


def collect():
    entries = []
    for directory in DIRECTORIES:
        for path in sorted((ROOT / directory).glob("*.po")):
            entries.append(entry_for(path))
    entries.sort(key=lambda item: (item["kind"], item["id"]))
    return entries


def main():
    entries = collect()
    old = {}
    if CATALOG.exists():
        try:
            old = json.loads(CATALOG.read_text(encoding="utf-8"))
        except ValueError:
            old = {}
    if old.get("entries") == entries:
        print("catalog.json 无需更新（%d 条）" % len(entries))
        return 0

    catalog = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entries": entries,
    }
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("catalog.json 已更新（%d 条）" % len(entries))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as error:
        print("错误：%s" % error, file=sys.stderr)
        sys.exit(1)
