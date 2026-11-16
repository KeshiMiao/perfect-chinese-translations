# 目录格式

`catalog.json` 由 `scripts/build_catalog.py` 扫描 `locale/*.po` 与 `blender/*.po` 生成，客户端只读取这一个
文件。CI 在推送到 `main` 后重新生成并提交；PR 只生成一次用于校验，不会提交。

## .po 文件头

文件头是开头的 `# key: value` 注释块；脚本读到第一行非注释内容就停止，后面的注释不再当元信息。

- 扫描范围只有 `locale/`（`kind=addon`）与 `blender/`（`kind=blender`），只收 `*.po`。
- 必填：`id`、`name`。首行 `# perfect-chinese: 1` 是格式标记，脚本目前不校验。
- `id` 必须匹配 `[a-z0-9][a-z0-9._-]*`，并且与文件名（去掉 `.po`）一致。
- `kind` 缺省按目录推断；补缺包必须写 `supported_versions`，不能留 `*`。
- `locale` 固定为 `zh_HANS`，写别的值会被拒绝。
- 单个 `.po` 不超过 512 KiB。
- `url`、`sha256`、`bytes` 由脚本按真实文件计算，不需要手写；其余字段原样进目录。
- `updated_at` 不写时取该文件最后一次 git 提交日期（格式 `YYYY-MM-DD`）。

```po
# perfect-chinese: 1
# id: texel-kit
# kind: addon
# module: bl_ext.blender_org.texel_kit
# name: Texel Kit
# name_zh: 纹素工具
# translator: KeshiMiao
# category: UV
# supported_versions: >=4.2.0
# updated_at: 2026-11-14
msgid ""
msgstr ""
"Language: zh_HANS\n"
"Content-Type: text/plain; charset=UTF-8\n"
```

## catalog.json 字段

```json
{
  "schema_version": 1,
  "generated_at": "2026-11-16T01:38:56Z",
  "entries": [
    {
      "id": "texel-kit",
      "kind": "addon",
      "module": "bl_ext.blender_org.texel_kit",
      "name": "Texel Kit",
      "name_zh": "纹素工具",
      "translator": "KeshiMiao",
      "category": "UV",
      "locale": "zh_HANS",
      "translation_version": "",
      "supported_versions": ">=4.2.0",
      "url": "locale/texel-kit.po",
      "sha256": "…",
      "bytes": 4347,
      "updated_at": "2026-11-14"
    }
  ]
}
```

- `entries` 按 `(kind, id)` 排序；条目没有变化时脚本不改文件，避免只有 `generated_at` 变化。
- `sha256` / `bytes` 用于下载校验；`url` 是仓库内相对路径。
- 客户端会校验：`id` 规则、`sha256` 为 64 位小写十六进制、`url` 不能以 `/` 开头 / 不能含 `..` / 不能带
  `://`、`bytes` 不超过 512 KiB、`supported_versions` 能被解析、`locale` 为 `zh_HANS`。单条不合法会被跳过并
  记入 `problems`；`schema_version` 高于客户端支持的版本时整个目录被拒绝（需要升级客户端）。
- 变更识别只看 `sha256`：文件内容一变，哈希就变，客户端据此判断是否更新，不需要人工递增版本号。
  `translation_version` 与 `updated_at` 不参与判断；`updated_at` 仅用于展示，并在补缺包版本区间重叠时用于
  取较新的一条。

## 版本区间

支持 `*`、裸版本号（前缀匹配，`4.5` 命中 4.5.x）、比较符组合（空格分隔为 AND）：
`>=4.5.0 <5.0.0`。不支持 `^`、`~`、`||`。写错的话 CI 会报错，客户端也会把该条判为版本不匹配。

## 翻译完成度

空 `msgstr`、`fuzzy`、`obsolete` 条目都不算已翻译；复数条目要求 `msgstr[0]` 存在，写出的所有复数形式都非空。

## 补缺包

`blender/blender-4.5.po`、`blender/blender-5.x.po`，分别声明 `>=4.5.0 <4.6.0`、`>=5.0.0 <6.0.0`。
两份文件目前各 766 / 790 条词条：731 条相同，仅 4.5 有 35 条、仅 5.x 有 59 条，所以必须分开放。

骨架由 `scripts/extract_blender_strings.py` 在 Blender 内抽取（只收 RNA 能枚举到的标题、提示与枚举项，
再减去官方 `zh_HANS` 已有的译文），动态拼接的文本不会出现在里面。

## 推送后自查

```bash
curl -sS https://raw.githubusercontent.com/KeshiMiao/perfect-chinese-translations/main/catalog.json
sha256sum locale/<id>.po   # 与目录里的 sha256、bytes 对比
```

`sha256` 与文件内容不一致时，客户端会把它当成一次更新。
