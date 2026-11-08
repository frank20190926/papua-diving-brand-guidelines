# Contest 2801171 — Codex 本地交付记录

2026-11-08。本次明确授权为本地生成，未提交平台、未发布、未提交 Git。没有调用子代理、agy 或 Claude；工作区内其他模型文件保持原样。

## 已交付

- `build_guidelines_2801171.py`：可重复生成全部指定资产、手册、HTML 和 ZIP。
- `exports/Papua_Diving_Resorts_Brand_Guidelines_2026.pdf`：19 页 A4，可打印；目录书签、嵌入字体、矢量纹样。
- `exports/Papua_Diving_Resorts_2026_Brand_Kit.zip`：PDF、ASE、3 SVG、3 PNG、原 Logo、数值色表、4 个字体、2 份 OFL 许可、说明与校验和，共 18 个文件。
- `board1-codex.html` 至 `board4-codex.html`：1600×1200 固定展示画布，依赖同目录 `boards-codex.css` 与本地 `assets/` / `exports/`，PDF 和 ZIP 链接可用。
- `exports/board-previews/`：四张 Chrome 实际渲染截图。

## 要求与证据

| 要求 | 结果 |
|---|---|
| 原 Logo 不变 | 原图与打包图 SHA-256 相同：`8900e4d513b5e98575fab1f88f2ef333f3ff5c278cc9c312da75751bb55c1bd8`。保留原有白色不透明底，不作抠图或改色。 |
| 1x / 32mm / 120px / 深色底托形 | 手册 3–5 页；展示板 2。封面实际 Logo 宽 91pt，约 32.1mm；应用小样标为缩小示意。 |
| 主色与双度假村区别 | 手册 6–8 页及 `Colour_Specifications.json`，全部 HEX/RGB/CMYK 按指定数值。 |
| ASE | 发现旧文件含过期蓝/雾色。备份在 `tmp/pdfs/Papua_Diving_Resorts_2026_Master_Palette.before.ase`；交付版含 9 个当前颜色 × RGB/CMYK 两组，共 18 色样，重新解析逐项核值。 |
| 字体 | Tenor Sans Regular；Source Sans 3 Regular / Medium / SemiBold。`pdffonts` 确认全部嵌入、子集化且具 Unicode 映射。 |
| 纹样 | SVG 无 image/text 节点；透明 PNG 为 4800×640、4800×520、1200×1200；有 300ppi 元数据。 |
| 完整手册 | 品牌原则、Logo、颜色、字体、语气、影像、纹样、应用、禁用项、制作及来源说明。 |
| PDF 视觉验证 | PyMuPDF 与 Poppler 均成功渲染全部 19 页，已目检；无渲染错误、文字越页或缺字。 |
| HTML 验证 | 普通 Chrome 经 osascript 操作；画布为 1600×1200，屏幕以 60% 缩放检查；字体加载、图片加载、画布边界检查通过，四板截图目检。审查窗口已关闭。 |
| 文件完整性 | ZIP CRC 与包内 SHA256SUMS 对照通过，ASE 与当前文件一致。 |

验证明细：`exports/build-validation.json`、`exports/board-validation.json`。

## 原件依据与制作边界

已直接提取并阅读四份雇主 PDF；已查看所给 bark paintings、内饰与文化参考及原 Logo。采用本轮指定的字体和 Logo 参数，优先于早期 PDF 的探索稿。

新纹样为基于原件的 bark-inspired 原创几何，不声称获得文化认证；沿用原件中的当地文化审核说明。PDF 为 A4 印刷参考手册，不是 PDF/X 或已完成印厂分色的生产稿。照片及 Logo 保留源像素，扩大印刷仍需业主提供高清摄影和正式矢量 Logo。CMYK 是给定目标值，实际纸张效果需打样。

AGENTS 漂移提示已只读比较：共享 canonical 正文完整包含于 Codex 目标文件；项目 AGENTS 存在既有修改，本次未覆盖。未改记忆文件。
