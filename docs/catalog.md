# 目录格式

`catalog.json` 由 `scripts/build_catalog.py` 生成，客户端只读取这个文件。

## catalog.json

```json
{
  "schema_version": 1,
  "generated_at": "2026-11-14T00:00:00Z",
  "entries": [
    {
      "id": "edgeflow",
      "kind": "addon",
      "module": "EdgeFlow",
      "name": "Edge Flow",
      "name_zh": "边流动",
      "translator": "可是",
      "category": "建模",
      "locale": "zh_HANS",
      "translation_version": "1.0.0",
      "supported_versions": ">=0.5.0 <1.0.0",
      "url": "locale/edgeflow.po",
      "sha256": "…",
      "bytes": 12345,
      "updated_at": "2026-11-14"
    }
  ]
}
```

- `id`：`[a-z0-9][a-z0-9._-]*`，同时是文件名（不含扩展名）。
- `kind`：`addon`（插件）或 `blender`（官方界面补缺包）。
- `supported_versions`：Blender 版本区间，写法见下。
- `url`：仓库内相对路径，禁止绝对路径与 `..`。
- `sha256` / `bytes`：由 CI 计算，客户端用来校验下载是否完整。
- 空 `msgstr`、`fuzzy`、obsolete 条目不计入翻译完成度。

## .po 文件头

```po
# perfect-chinese: 1
# id: edgeflow
# kind: addon
# module: EdgeFlow
# name: Edge Flow
# name_zh: 边流动
# translator: 可是
# category: 建模
# translation_version: 1.0.0
# supported_versions: >=0.5.0 <1.0.0
# updated_at: 2026-11-14

msgid ""
msgstr ""
"Language: zh_HANS\n"
"Content-Type: text/plain; charset=UTF-8\n"
```

必填：`id`、`name`、`translation_version`。`kind` 缺省按路径推断（`blender/` 下为 `blender`）。

## 版本区间

支持 `*`、裸版本号（前缀匹配，`4.5` 命中 4.5.x）、比较符组合（空格分隔为 AND）：
`>=4.5.0 <5.0.0`。不支持 `^`、`~`、`||`。

## 补缺包

`blender/blender-4.5.po`、`blender/blender-5.x.po`，分别用 `supported_versions` 声明
`>=4.5.0 <4.6.0`、`>=5.0.0 <6.0.0`。两版词条不同（实测仅 4.5 有 1,714 条、仅 5.2 有 4,497 条），必须分开。
