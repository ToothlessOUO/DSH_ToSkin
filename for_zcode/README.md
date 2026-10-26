# ZONE skin for ZCode

黑橙硬件风 [ZCode](https://zcode.ai) 桌面端皮肤 —— DSH ZONE 皮肤（`../package/`）的
ZCode 同款移植：石墨机身、热橙强调、奶油键帽纸、模切贴纸几何、警戒条纹与 LED
设备条，四套配色（zone / ember / hazard / cobalt）× 两块画布（blacksite / cream）。

ZCode 没有客户端插件槽位，所以移植走 **app.asar 注入** 路线（本仓库外层
`~/.zcode/custom-ui/` 早已验证过的机制）：解包官方 `resources/app.asar`，注入
`zone.css` + `zone-boot.js`，修补 `index.html`，重打包。全程不改任何应用逻辑，
`tools/restore.cmd` 一键还原。

## 它改了什么

- **颜色** —— ZCode 是 Tailwind v4，整个 UI 从 `<html>` 上的语义变量取色。
  皮肤在 `html[data-zone-skin]` 上重写这些 `--color-*` token：blacksite 画布是
  暖石墨 `#2c2927`（卡片 `#373330`、浮层 `#423d3a`），cream 画布是键帽米白
  `#e8e1d1`（卡片 `#f5efe4`），正文墨水恒为奶油白 / 深墨，主按钮与焦点环取配色
  强调色，4–12px 的厚实圆角，深橙投影。侧栏、菜单、弹层、对话框、tooltip、
  终端底盘、图表色板、"highspeed" 模式的紫色强调全部随画布与配色联动。
- **字体** —— UI 面是 Bahnschrift，标签面是 Cascadia Mono，中文由
  Noto Sans Mono CJK SC 承担（与 DSH 版同一字体栈、同一装机前提，见下）。
- **用户消息板** —— 聊天里用户消息的容器就是配色强调色本身，墨水恒白
  （`--zone-brand-on: #ffffff`，一处字面量统领所有亮板），板内选区反白保持可见。
  与 DSH 版同一规则：亮板上只有一种白。
- **氛围层** —— 固定层绘制 7px 半调网点、左侧 30px 侧栏投影、四只配色托架
  胶带角，以及跟随指针的方形网点透镜（亮头 + 迟滞尾，出聊天区淡出）。
- **控制台** —— 左下角常驻一枚 `ZONE/0n` 芯片，点开是完整面板：奶油贴纸
  （ZONE + 警戒带 + 四色样块）、配色 / 画布 / 动效按钮行、半调开关、LED 设备条
  （脉冲灯 + 警戒带 + 配色编号 R1 + 图纸号）。快捷键：`Ctrl+Alt+Z` 换配色、
  `Ctrl+Alt+X` 换画布、`Ctrl+Alt+H` 隐藏 / 唤出控制台。
- **光标** —— 24px SVG 自绘指针集（石墨箭头 + 配色描边、奶油描边的线稿字形），
  随配色与画布切换；`wait`/`help` 等系统态保持原生。

## 两块画布 × 四套配色

| 画布 | 底面 | 文字 |
| --- | --- | --- |
| Blacksite（夜，跟随应用的暗色主题） | 石墨 `#2c2927` / 卡片 `#373330` | 奶油 `#f8f3e8` |
| Cream（昼，跟随应用的亮色主题） | 键帽米白 `#e8e1d1` / 卡片 `#f5efe4` | 深墨 `#171310` |

| 配色 | 夜 · 强调 | 昼 · 强调 |
| --- | --- | --- |
| Zone orange | `#ff6f1a` | `#e2560d` |
| Ember | `#ff4632` | `#c62c1b` |
| Hazard | `#ffc61a` | `#a8770a` |
| Cobalt | `#4d94ff` | `#1f5fd6` |

机身永远不随配色变化 —— 只有强调色动，和硬件配色一个道理。画布三挡：
`auto`（跟随应用主题，`<html>` 上 `dark` 类翻转时实时跟随）/ `cream` / `blacksite`；
强制一挡会把应用的亮暗两种主题都映射到同一块画布。

偏好存在渲染进程 `localStorage` 的 `zcode-zone-skin:prefs`（多窗口经 storage
事件同步）；`prefers-reduced-motion` 永远优先于皮肤动效设置。

## 安装（Windows）

0. **中文字体**（每台机器一次，包里不带这 31.8 MB 的 OTF）：

   ```powershell
   powershell -ExecutionPolicy Bypass -File ..\font-lab\install-fonts.ps1
   ```

   装完**重启 ZCode**——渲染进程只在启动时枚举系统字体。

1. 构建（解包 → 注入 → 校验，产物不出 `tools/out/`）：

   ```sh
   cd for_zcode/tools
   npm install        # 或者：已存在 ~/.zcode/custom-ui/node_modules 时可跳过
   node build.js
   ```

2. 应用：双击 `tools/apply.cmd`（管理员），然后**完全退出 ZCode
   （托盘右键退出）再打开**。首次 apply 会把当前官方包备份为
   `tools/out/app.asar.zone-bak`。
3. 还原：双击 `tools/restore.cmd`。

ZCode 升级会覆盖 `app.asar`，重新跑一遍 `node build.js` + `apply.cmd` 即可；
构建脚本用正则找样式表锚点（`styles-<hash>.css` 的 hash 每个版本都变），
结构大变时会拒绝注入而不是打坏包。

## 离线试验台

`testbed/` 用最少的假结构（主题变量作用域 + 皮肤选中的几个结构钩子）加载
**未修改的** `zone.css` + `zone-boot.js`，配合右上角按钮切换主题 / 配色，
用于不动应用就能做视觉验收：

```sh
node testbed/serve.mjs 8472
# 打开 http://127.0.0.1:8472/testbed/?theme=zai-dark&colorway=zone
```

## 检查

```sh
cd for_zcode
node --check zone-boot.js
node tests/token-contrast.mjs   # 色板完整性 + 对比度地板（正文 7:1 / 次级 4.5:1 / 弱化 3:1）
node tests/css-coverage.mjs     # 大括号平衡；boot 渲染的类都有样式；var() 全部可解析
```

`css-coverage` 里的 `tests/app-token-names.json` 是从**当前安装的**
`styles-9Z13W0KP.css` 提取的 token 清单 —— 每个被皮肤改写的 `--color-*` 都必须在
里面，否则那个变量名就是打错了（声明会被静默丢弃，见 NOTES.md）。

## 与 DSH 版的差异

| DSH 版 | ZCode 版 | 原因 |
| --- | --- | --- |
| Cordis 插件（host/client 双半、五个槽位） | app.asar 注入（CSS + boot 脚本） | ZCode 无插件 UI 槽位 |
| token 层跑在 `ctx.theme.overrideTokens()` | token 层是纯 CSS（`color-mix()` 运行时推导） | 免构建即可改色 |
| 设置页在 Settings → General | 控制台面板（左下芯片）+ 快捷键 | 无设置页注入口 |
| 完成提示音（api-session 投影） | 无 | 无事件桥可挂；见 NOTES.md |
| 氛围层锚定会话面板（运行时测量） | 氛围层全窗，顶角托架按 chat-view 测量 | 无 shell.overlay 座位 |
| 侧栏选中会话行 = 实心配色板 | 选中行取 `--color-selected`（配色软染） | 行级结构钩子待实测确认 |
| 哈希 CSS Modules 类名 | `data-slot` / `data-testid` 语义钩子 | ZCode 是 Tailwind + shadcn |

## 文件

| 文件 | 作用 |
| --- | --- |
| `zone.css` | 皮肤本体：色板输入 → 画布解析 → 派生 token → 语义映射 → 样式层 |
| `zone-boot.js` | 客户端半：偏好、根属性、光标、氛围层、控制台、探测器 |
| `tools/build.js` | 解包 → 注入 → 修补 index.html → 重打包 → 校验 |
| `tools/apply.cmd` / `restore.cmd` | 安装（管理员）/ 还原 |
| `tests/` | token 对比度 + 样式覆盖率 |
| `testbed/` | 离线视觉验收台 |
| `NOTES.md` | 排错现场笔记 —— 改颜色前先读 |
| `AGENTS.md` | 接手本目录的 agent 须知 |

## 许可

皮肤代码 MIT（同 DSH 版）。中文字体不在本目录内，遵守其上游许可
（`../font-lab/` 内 Noto 为 SIL OFL 1.1）。
