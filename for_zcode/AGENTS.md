# AGENTS.md — 接手 for_zcode 前必读

给冷启动接手这个目录的 agent（或人）。

## 这是什么

DSH ZONE 皮肤（`../package/`，Cordis 客户端插件）的 **ZCode 同款移植**。
ZCode 是 Electron 应用，没有插件 UI 槽位，所以载体换成了 app.asar 注入：

1. **token 层（CSS）** —— `zone.css` 在 `html[data-zone-skin]` 上重写 ZCode 的
   Tailwind v4 语义变量（`--color-*`），派生色全部用 `color-mix()` 运行时算，
   色板输入集中在一个块里；
2. **样式层（CSS）** —— 同文件后半：选区钉子、用户消息板、composer 背光、
   光标规则、`.zone-*` 皮肤 DOM 的样式；
3. **boot 层（JS）** —— `zone-boot.js`：偏好、根属性、光标变量、氛围层 DOM、
   控制台、探针。全部挂在 `#root` 之外，React 不会碰。

`tools/build.js` 把 1+2+3 注入 `resources/app.asar`。一切视觉都出在这三层；
颜色"不生效"时先判断该归哪层管。

## 环境事实（2026-10-26，Windows，ZCode 桌面版实测）

| 事实 | 值 |
| --- | --- |
| 安装目录 | `C:\Program Files\ZCode\resources\app.asar`（可用 `ZCODE_RESOURCES` 覆盖） |
| 渲染层入口 | `out/renderer/index.html` + `out/renderer/assets/styles-<hash>.css` |
| 当前锚点 | `styles-9Z13W0KP.css`（hash 每版本变，**必须正则匹配**） |
| 主题模型 | `localStorage['zcode-theme']`：`system\|dark\|light\|zai-dark\|zai-light`，默认 `zai-dark`；`<html>` 上的类：`dark` + `theme-zai-*` |
| asar 库 | `@electron/asar` 4.3.1，**ESM-only**（`import()`，别 `require()`）；本目录 `tools/npm install`，或回退 `~/.zcode/custom-ui/node_modules` |
| 重打包 | asar 4.x 默认文件去重（包小 30+ MiB 是正常的）；`unpack: '*.{node,dll,exe}'` 保持原生二进制外置 |
| 中文字体 | 前提是机器级安装（`../font-lab/install-fonts.ps1`），渲染进程启动时枚举，装完要重启 |
| 生效方式 | apply 后**完全退出**（托盘右键）再启动；asar 不是热加载 |

## 校验环

```sh
node --check zone-boot.js          # boot 语法
node tests/token-contrast.mjs      # 色板 + 对比度地板
node tests/css-coverage.mjs        # 覆盖率 + var() 可解析性
cd tools && node build.js          # 产出 tools/out/app.asar.zone（不安装）
node ../testbed/serve.mjs 8472     # 离线视觉验收（不改应用就能看）
```

测试全绿 + 构建校验通过 + 试验台看过四种状态（夜/昼 × 两配色）再交付。
`apply.cmd`（写 Program Files）永远留给用户自己双击。

## 不变量 —— 破坏任何一条皮肤都会静默变丑

1. **亮板墨水是字面量白**。`--zone-brand-on: #ffffff` 与
   `--color-primary-foreground: #ffffff` 不许改成推导值；夜间 zone 橙 2.78:1、
   夜间 hazard 黄 1.57:1 是 owner 接受过的取舍（DSH 版同样），token-contrast
   会把它作为 note 打出来而不是 FAIL。反之 `success/warning-foreground`
   这类**功能色墨水**必须守住 3:1（夜success 用深墨 `#14110d` 是测试抓出来的）。
2. **用户消息板 = 配色本身**，没有第二张手挑的板色表；板内上墨靠局部重定义
   `--color-foreground` 系，不靠 `!important` 链。板内选区反白必须 `!important`。
3. **画布四规则的源顺序**：day 默认 → `.dark` 翻夜 → 强制夜 → 强制昼。
   同特异性靠顺序决胜。
4. **阴影只用 `rgb(var(--zone-shade-rgb) / α)`**，不让 `color-mix()` 进
   box-shadow——一个坏 mix 会作废整条 shadow 列表。8 组 rgb 三元组在
   colorway 块里，token-contrast 逐组对账。
5. **覆盖的 `--color-*` 必须在 `tests/app-token-names.json` 里**（从安装的
   `styles-9Z13W0KP.css` 提取）。应用升级后重新提取这份清单再跑测试。
   唯一白名单：`--color-ring`（应用引用未定义，皮肤有意补上）。
6. **结构钩子只用字面量**（`data-slot` / `data-testid` / `data-*`），哈希
   前缀和 `class*=` 子串一个都不许进本目录的 CSS。新增钩子前先在真机
   devtools 确认（见 NOTES.md 的钩子清单）。
7. **boot 的 DOM 全部挂在 `#root` 外**、氛围层 `pointer-events:none`、
   z-index 低于 2147483647（splash）。别让皮肤 DOM 参与应用的布局树。

## 当前状态（交接下去）

- 已验证：两画布 × zone/cobalt 的试验台截图、token/coverage 测试、
  build 端到端（列表对账 + 6 文件哈希抽查 + unpacked 三方一致）。
- 已于 2026-10-26 应装到真机（等效 apply.cmd 的备份+拷贝，装前确认官方包未
  打补丁、装后校验 +2 文件与 index.html 三处注入）。**重启后尚未由用户目检**；
  首次重启后按 NOTES.md 的排错清单过一遍，探针键 `zcode-zone-skin:probe`。
  回滚：`tools/restore.cmd`（备份在 `tools/out/app.asar.zone-bak`）。
- 已知未做（原因见 NOTES.md）：完成提示音、侧栏选中行实心板、toast 染色。
- 旧版毛玻璃皮肤（`~/.zcode/custom-ui/`）与本皮肤共用注入机制但互不知晓：
  若它还在应用中，先用它的 restore 还原官方包再 apply 本皮肤；两个皮肤的
  backup 文件名不同（`app.asar.bak` vs `app.asar.zone-bak`），不要混用。

## 文件图

| 文件 | 角色 |
| --- | --- |
| `zone.css` | token 层 + 样式层（皮肤本体，改色从"palette inputs"块进） |
| `zone-boot.js` | 客户端半：偏好/属性/光标/氛围/控制台/探针 |
| `tools/build.js` | 解包 → 注入 → 修补 → 重打包 → 校验（不安装） |
| `tools/apply.cmd` / `restore.cmd` | 用户手动的安装 / 还原（管理员） |
| `tests/token-contrast.mjs` | 色板完整性 + 对比度地板 + rgb 三元组对账 |
| `tests/css-coverage.mjs` | 大括号/类覆盖/var() 可解析/被覆盖 token 存在性 |
| `tests/app-token-names.json` | 安装版样式表的 token 清单（升级后重新提取） |
| `testbed/` | 离线验收台（serve.mjs + 假结构页） |
| `README.md` / `NOTES.md` | 使用说明 / 排错笔记 |
