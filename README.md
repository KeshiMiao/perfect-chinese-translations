# perfect-chinese-translations

[完美中文](https://github.com/KeshiMiao/perfect-chinese) 的翻译内容仓库。

- 只提供**译文**（及其对应的原文），不包含任何插件本体。
- 每个翻译文件是一个 `.po`，本地化固定 `zh_HANS`，文件头写明元信息（见 `docs/catalog.md`）。
- `catalog.json` 由 CI 从 `.po` 生成，客户端只读它。

## 目录

```text
catalog.json                        # 目录索引（CI 生成，勿手改）
locale/*.po                         # 插件翻译
blender/*.po                        # Blender 官方界面补缺包（按大版本拆）
scripts/build_catalog.py            # 扫描 .po 生成 catalog.json
scripts/extract_blender_strings.py  # 在 Blender 内抽取补缺包骨架
docs/catalog.md                     # 文件头、目录字段与校验规则
```

## 新增一个插件翻译

1. 在 `locale/` 放 `<id>.po`，`id` 用小写、与文件名一致；文件头写明 `id`、`name` 等元信息
   （字段见 `docs/catalog.md`）。
2. 提交 PR：CI 会生成一次目录用于校验；合并到 `main` 后 CI 重新生成并提交 `catalog.json`。

## 维护补缺包

`blender/blender-4.5.po` 与 `blender/blender-5.x.po` 分别对应 Blender 4.5 与 5.x，由
`scripts/extract_blender_strings.py` 在对应版本的 Blender 里生成骨架后再补译：

```bash
blender -b --factory-startup --python scripts/extract_blender_strings.py -- out.po
```

两版词条不同，不要合并；文件头的 `supported_versions` 必须写明版本区间。

## 许可

本仓库的脚本、目录与译文以 [GPL-3.0-or-later](LICENSE) 发布；译文所对应的插件/软件作品仍归其原作者，译文不改变原作的许可，也不包含任何原作代码。

译文由社区贡献。原作者如有异议，请在 Issues 中说明，我们会下架对应条目。
