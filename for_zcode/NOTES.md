# NOTES — ZCode 版皮肤的排错现场笔记

从 DSH 版移植时踩过、想明白、或只能折衷的地方。改颜色之前先读这份；
DSH 版的 [../package/NOTES.md](../package/NOTES.md) 里关于 `var()` 静默失效、
`!important` 陷阱、探针优先的三条在这里同样成立。

## 注入模型：三层，一个都不许少

`tools/build.js` 对 `index.html` 做三件事：

1. `<html …>` 标签写入 `data-zone-skin` 等默认属性；
2. 应用样式表 `<link … styles-<hash>.css>` **之后**插入 `zone-skin.css`；
3. `</head>` 前插入 `<script src="zone-skin-boot.js" defer>`。

第 1 条是冗余保险：皮肤 CSS 的每个选择器都要求 `html[data-zone-skin]`，
若 boot 脚本因任何原因没跑，默认属性仍让 token 层生效（默认 zone / auto /
full）。boot 跑起来后接管这些属性。第 2 条的顺序就是级联：同特异性时后写的赢。

## 为什么选择器能保持稳定

DSH 的宿主用 CSS Modules，类名带每构建的哈希前缀（`wnFoaW_sessionRow`），
只能 `[class*="_sessionRow"]` 子串匹配。ZCode 完全不同：Tailwind v4 +
shadcn，界面从 `<html>` 上的语义变量取色，结构钩子是**字面量**：

- 主题类在 `<html>`：`dark`、`theme-zai-dark`、`theme-zai-light`
  （`localStorage['zcode-theme']`：`system|dark|light|zai-dark|zai-light`，默认 zai-dark）；
- shadcn 原语带 `data-slot="button|input-group|select-trigger|…"`；
- 聊天输入框是 `[data-testid="chat-input"]`——应用自己在十几个地方把它当
  focus 还原选择器用，是最稳的契约；
- 用户消息文本容器：`[data-v4-user-input-collapsible-content]`
  （会话流）与 `[data-trajectory-user-content-card]`（轨迹视图）；
- Markdown 代码块：`[data-streamdown="code-block"]`。

所以本皮肤**没有**一个 `[class*=…]` 哈希选择器；结构钩子只有上表四个。
`styles-<hash>` 的 hash 会随版本变，锚点必须正则匹配（build.js 已处理）。

## token 层为什么放在 `<html>` 上能赢

应用自己的语义块是 `.theme-zai-light` / `.theme-zai-dark`（0,1,0）和
`.dark`（0,1,0）、`.dark,.theme-zai-dark`（0,2,0）。皮肤的块：

- `html[data-zone-skin]`（0,1,1）→ 压过两个主题块；
- `html[data-zone-skin].dark` 与 `html[data-zone-skin][data-zone-canvas=…]`
  （0,2,1）→ 压过 `.dark,.theme-zai-dark` 的高特权块。

四条画布规则的先后顺序是**故意的**：day 默认 → `.dark` 翻夜 → 强制夜 →
强制昼。同特异性靠源顺序决胜，别打乱这个顺序。组件局部重定义的语义变量
（目前没发现）仍会赢过皮肤 —— 这是对的，别用 `!important` 去填。

## 高特权却又没定义的 `--color-ring`

应用代码里有 `focus-visible:ring-ring/50` 这类工具类，但样式表**从未定义**
`--color-ring` —— 那些声明算出无效值后被静默丢弃，焦点环退回 Tailwind 的
currentColor 默认。皮肤有意定义它为配色强调色（对应 DSH 的 focus-ring），
这是"补上被丢弃的声明"而不是"覆盖既有值"。css-coverage 测试里它是唯一的
白名单项，别往白名单里加第二个。

## 氛围层：z-index 与命中

氛围层是 `position:fixed; inset:0; z-index:2147483000; pointer-events:none`。
必须盖过内容（网点是纸面纹理），又必须低于启动 splash（`#loading` 是
2147483647）。`pointer-events:none` 保证它不拦截任何点击——测过
`elementFromPoint` 命中正确。控制台芯片是唯一可交互的皮肤 DOM，
z-index 2147483646，同样低于 splash。

应用表面是不透明的：任何想画在内容**下面**的氛围都会整个看不见。
DSH 版把氛围锚定到会话面板是因为它有 `shell.overlay` 槽位；这里没有，
全窗固定层 + 顶角托架用 `--zone-content-top`（boot 每 2s 测
`[data-testid="chat-view"]` 顶缘，找不到回退 0）下移，避开应用自绘标题栏。

## 用户消息板：用变量作用域上墨，而不是 `!important`

DSH 版给板内文字上白墨靠的是 `--zone-plate-ink` + 一串 `!important`。
这里更干净：板元素上**局部重定义** `--color-foreground` 系列为白色，板内所有
`text-foreground` 工具类自动解析成白 —— owner 的规则一条没动。板的选区
反白仍然要 `!important`（压过全局的强调色选区钉子），和 DSH 版同理：
强调色选区落在强调色板上会凭空消失。

已知边界：`data-v4-user-input-collapsible-content` 的折叠逻辑测量的是
`scrollHeight`，皮肤加的 padding 会被一起量进去，折叠阈值不受影响 ——
但若某天移植新版发现折叠按钮位置怪了，先查这里。

## 折衷与未移植项（都有原因，别"顺手补"）

- **完成提示音没移植。** DSH 版骑在宿主转发的 `api-session/*` 投影上；
  ZCode 渲染进程没有等价的事件桥（`ZCODE_E2E_STORE_BRIDGE` 是 E2E 测试门，
  不是扩展面）。想加提示音得先找到稳定的运行时信号，别往 boot 里塞轮询。
- **侧栏选中会话行没有上实心配色板。** 侧栏行通过 `--color-selected`
  拿到配色的软染（`mix(layer1, brand, 18%)`），但要复刻 DSH 的"选中 = 实心
  强调板"需要行级钩子。侧栏行的 `data-active` 用法在源码里看到多处
  （side-pane 标签、turn navigator），没能确认侧栏任务行本身 —— 在真机
  devtools 里确认钩子后再加，不要猜。
- **toast 没有染成强调色。** DSH 的 toast 是"贴纸橙"面板 + 专属墨水
  token；ZCode 的 `--color-toast` 只有表面一个变量，墨水走全局前景，
  染橙会在昼画布上做出橙底深墨的奇怪组合。保持中性表面。
- **终端只动了底盘 / 光标 / 选区。** 16 色 ANSI 是可读性语义，保持原样；
  DSH 版没有终端 token，无从对齐。

## 构建管线的三个坑

- **@electron/asar 4.x 是 ESM-only**：`require()` 它会报 MODULE_NOT_FOUND；
  build.js 用 `import('file://…/lib/asar.js')` 动态导入。
- **asar 4.x 重打包默认去重**：相同内容的文件共享偏移（实测省 32.7 MiB，
  包从 325.6 MiB 变 292.9 MiB）。Electron 的读取器按 offset+size 读，
  重叠透明，已抽查 6 个文件哈希一致。**不要**把"包变小"当成丢文件——
  build.js 的校验按文件列表对账。
- **原包头记录的 13 个 unpacked 原生文件 size 是陈旧的**（node-pty/ssh2，
  签名后没回头改包头）。磁盘上 `app.asar.unpacked/` 才是真身，逐字节哈希
  三方一致（orig == work == out）。校验逻辑以磁盘与列表为准，不比包头 size。

## 排错清单（"皮肤坏了"先过这六条）

1. `html` 上有没有 `data-zone-skin`？（boot 死了也有 install 时的默认属性兜底）
2. `zone-skin.css` / `zone-skin-boot.js` 两个文件在不在包里？
   （devtools: `document.querySelector('link[href*="zone-skin"]')`）
3. boot 活着吗？（console 里 `window.__zoneSkinBooted` / `window.ZONE_SKIN.rev`）
4. `<html>` 的主题类是什么？`auto` 画布跟着 `dark` 类走，应用主题切了皮肤必须跟着翻。
5. 那个元素读的变量真的解析了吗？（css-coverage 的 token 清单就是干这个的）
6. 应用升级过？hash 锚点变了会让 build.js 拒绝注入 —— 重跑 build，别手动改包。

## 探针

devtools console：

```js
localStorage['zcode-zone-skin:probe'] = '1';   // 然后完全重启 ZCode
```

2.5 秒后 `localStorage['zcode-zone-skin:diag']` 里是一次性的体检报告：boot
是否活、`<html>` 主题类、`--zone-brand` 在 html/body 上的解析值、氛围层 /
控制台 / 聊天输入框的矩形、用户消息板的实算背景色与文字色、当前偏好。
读完 `removeItem` 关掉。它只写这一个键，不动文档。
