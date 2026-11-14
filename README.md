# perfect-chinese-translations

[完美中文](https://github.com/KeshiMiao/perfect-chinese) 的翻译内容仓库。

- 只提供**译文**（及其对应的原文），不包含任何插件本体。
- 每个翻译文件是一个 `.po`，本地化固定 `zh_HANS`。
- `catalog.json` 由 CI 从 `.po` 生成，客户端只读它。

## 目录

```text
catalog.json          # 目录索引（CI 生成，勿手改）
locale/*.po           # 插件翻译
blender/*.po          # Blender 官方界面补缺包（按大版本拆）
scripts/build_catalog.py
docs/catalog.md       # 字段说明与校验规则
```

## 新增一个插件翻译

1. 在 `locale/` 放 `插件 id.po`，文件头写明元信息（见 `docs/catalog.md`）。
2. 提交后 CI 重新生成 `catalog.json`。

## 许可

本仓库的脚本、目录与译文以 [GPL-3.0-or-later](LICENSE) 发布；译文所对应的插件/软件作品仍归其原作者，译文不改变原作的许可，也不包含任何原作代码。

译文由社区贡献。原作者如有异议，请在 Issues 中说明，我们会下架对应条目。
