"""在 Blender 内运行：抽取内置界面的英文词条，生成补缺包的 .po 骨架。

用法（需要 Blender 可执行文件）：
    blender -b --factory-startup --python scripts/extract_blender_strings.py -- out.po

只收集 RNA 能枚举到的词条（属性名/描述、枚举项、面板与运算符的标题/提示），
再减去官方 zh_HANS 目录里已有译文的条目。动态拼接的文本无法枚举，不在其中。
"""

import gettext
import os
import re
import sys

import bpy

IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:+\-/ ]+$")
IDENT_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_.]*$")
SKIP_WORDS = ("translation context", "RNA doc", "Internal API")
MAX_LEN = 220


def official_catalog():
    root = bpy.utils.resource_path("LOCAL")
    path = os.path.join(root, "datafiles", "locale", "zh_HANS", "LC_MESSAGES", "blender.mo")
    if not os.path.exists(path):
        return {}
    with open(path, "rb") as handle:
        return gettext.GNUTranslations(handle)._catalog


def wanted(text):
    if not text:
        return False
    text = text.strip()
    if len(text) < 2 or len(text) > MAX_LEN:
        return False
    if not any(ch.isalpha() for ch in text):
        return False
    if "_" in text and " " not in text:
        return False
    if IDENT_NAME.match(text) and text.islower():
        return False
    if text.isupper() and " " not in text:
        return False
    lowered = text.lower()
    return not any(word.lower() in lowered for word in SKIP_WORDS)


def translated(catalog, text, context=None):
    if text in catalog:
        return True
    return (context or "", text) in catalog


def collect():
    """{(msgctxt, msgid): 来源}，来源用于排查。"""
    found = {}
    catalog = official_catalog()

    def add(text, context, source):
        if not wanted(text):
            return
        if translated(catalog, text):
            return
        found.setdefault((context, text), source)

    classes = []
    for name in dir(bpy.types):
        obj = getattr(bpy.types, name)
        if isinstance(obj, type) and hasattr(obj, "bl_rna"):
            classes.append(obj)

    for cls in classes:
        try:
            rna = cls.bl_rna
        except Exception:
            continue
        is_operator = issubclass(cls, bpy.types.Operator)
        label = getattr(cls, "bl_label", "") or ""
        description = getattr(cls, "bl_description", "") or ""
        if is_operator and label:
            add(label, "Operator", rna.identifier)
            if description and description != label:
                add(description, "", rna.identifier)
        elif issubclass(cls, (bpy.types.Panel, bpy.types.Menu, bpy.types.Header)):
            if label:
                add(label, "", rna.identifier)
            category = getattr(cls, "bl_category", "") or ""
            if category:
                add(category, "", rna.identifier)
        for prop in rna.properties:
            if prop.identifier == "rna_type":
                continue
            add(prop.name, "", "%s.%s" % (rna.identifier, prop.identifier))
            add(prop.description, "", "%s.%s" % (rna.identifier, prop.identifier))
            if prop.type == "ENUM":
                try:
                    items = prop.enum_items
                except Exception:
                    items = []
                for item in items:
                    add(item.name, "", "%s.%s[%s]" % (rna.identifier, prop.identifier, item.identifier))
                    add(item.description, "", "%s.%s[%s]" % (rna.identifier, prop.identifier, item.identifier))
    return found


def quote(text):
    return '"%s"' % text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def dump(entries, path, version, supported):
    major, minor = version[0], version[1]
    pack_id = "blender-4.5" if major == 4 else "blender-%d.x" % major
    lines = [
        "# perfect-chinese: 1",
        "# id: %s" % pack_id,
        "# kind: blender",
        "# module: blender",
        "# name: Blender %d.%d" % (major, minor),
        "# name_zh: Blender %d.%d 界面补缺" % (major, minor),
        "# translator: KeshiMiao",
        "# category: 界面",
        "# supported_versions: %s" % supported,
        "# generated_by: scripts/extract_blender_strings.py",
        "msgid \"\"",
        "msgstr \"\"",
        '"Language: zh_HANS\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
    ]
    for (context, msgid), source in sorted(entries.items()):
        lines.append("")
        lines.append("#: %s" % source)
        if context:
            lines.append("msgctxt %s" % quote(context))
        lines.append("msgid %s" % quote(msgid))
        lines.append('msgstr ""')
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not argv:
        raise SystemExit("需要输出路径：-- out.po")
    version = bpy.app.version
    major = version[0]
    if major == 4:
        supported = ">=4.5.0 <4.6.0"
    else:
        supported = ">=5.0.0 <6.0.0"
    entries = collect()
    dump(entries, argv[0], version, supported)
    print("EXTRACTED %d -> %s" % (len(entries), argv[0]))


if __name__ == "__main__":
    main()
