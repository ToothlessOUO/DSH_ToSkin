/* ZONE skin for ZCode — build script (R1).
 *
 * 解包官方 app.asar → 注入 zone.css + zone-boot.js → 修补 index.html
 * → 重打包（保持原生二进制 unpacked）→ 校验文件列表。
 * 产物：for_zcode/tools/out/app.asar.zone（未直接安装；安装运行 apply.cmd）
 *
 * 与 2026-10 旧版 custom-ui/build.js 的差异：
 *   - 样式表锚点用正则匹配 styles-<hash>.css（hash 随版本变化，不能写死）；
 *   - 同时注入 <link>（在应用样式表之后，保证级联在后）和 <script defer>；
 *   - <html> 标签写入 data-zone-* 默认属性，boot 脚本失效时皮肤 CSS 仍生效；
 *   - asar 库解析顺序：本目录 node_modules → ~/.zcode/custom-ui/node_modules。
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const HERE = __dirname;
const SKIN = path.dirname(HERE);
const ZONE_CSS = path.join(SKIN, 'zone.css');
const ZONE_BOOT = path.join(SKIN, 'zone-boot.js');
const WORK = path.join(HERE, 'unpacked');
const OUT_DIR = path.join(HERE, 'out');
const OUT = path.join(OUT_DIR, 'app.asar.zone');
const BOOT_CSS_NAME = 'zone-skin.css';
const BOOT_JS_NAME = 'zone-skin-boot.js';

function die(msg) { console.error('[FAIL]', msg); process.exit(1); }
function log(step, msg) { console.log(`[${step}] ${msg}`); }

function loadAsar() {
  const candidates = [
    path.join(HERE, 'node_modules', '@electron', 'asar'),
    path.join(os.homedir(), '.zcode', 'custom-ui', 'node_modules', '@electron', 'asar'),
  ];
  for (const dir of candidates) {
    const entry = path.join(dir, 'lib', 'asar.js');
    if (fs.existsSync(entry)) {
      // @electron/asar 4.x is ESM-only; require() its lib through a dynamic import bridge.
      return import('file://' + entry.split(path.sep).join('/'));
    }
  }
  die('未找到 @electron/asar —— 先在 tools/ 下运行 npm install，'
    + '或确认 ~/.zcode/custom-ui/node_modules 存在。');
}

function findResourcesDir() {
  const override = process.env.ZCODE_RESOURCES;
  if (override) return override;
  const def = 'C:/Program Files/ZCode/resources';
  if (fs.existsSync(path.join(def, 'app.asar'))) return def;
  die('未找到 ZCode 安装目录（' + def + '）。可用环境变量 ZCODE_RESOURCES 指定 resources 目录。');
}

(async () => {
  const asar = await loadAsar();
  const RESOURCES = findResourcesDir();
  const ORIG = path.join(RESOURCES, 'app.asar');
  log('0/6', '资源目录: ' + RESOURCES);

  const css = fs.readFileSync(ZONE_CSS, 'utf8');
  const boot = fs.readFileSync(ZONE_BOOT, 'utf8');
  if (!css.includes('html[data-zone-skin]')) die('zone.css 内容异常（缺少 token 层）');
  if (!boot.includes('__zoneSkinBooted')) die('zone-boot.js 内容异常');

  // ---- 1. 全量解包 ----
  log('1/6', '解包 app.asar ...');
  fs.rmSync(WORK, { recursive: true, force: true });
  await asar.extractAll(ORIG, WORK);

  // ---- 2. 注入皮肤文件 ----
  log('2/6', '注入 ' + BOOT_CSS_NAME + ' + ' + BOOT_JS_NAME + ' ...');
  const assets = path.join(WORK, 'out', 'renderer', 'assets');
  if (!fs.existsSync(assets)) die('解包结果缺 out/renderer/assets —— 应用结构变了？');
  fs.writeFileSync(path.join(assets, BOOT_CSS_NAME), css);
  fs.writeFileSync(path.join(assets, BOOT_JS_NAME), boot);

  // ---- 3. 修补 index.html ----
  log('3/6', '修补 index.html ...');
  const idxPath = path.join(WORK, 'out', 'renderer', 'index.html');
  let idx = fs.readFileSync(idxPath, 'utf8');
  if (idx.includes(BOOT_CSS_NAME) || idx.includes(BOOT_JS_NAME)) {
    die('index.html 已包含 ZONE 注入 —— 目标 app.asar 似乎已打过皮肤补丁，拒绝重复注入。'
      + '若是旧皮肤（zcode-custom），请先运行其 restore.cmd 恢复官方包。');
  }
  const linkRe = /<link rel="stylesheet"[^>]*href="\.\/assets\/styles-[A-Za-z0-9_-]+\.css">/;
  const anchor = idx.match(linkRe);
  if (!anchor) die('未找到应用样式表 <link ... styles-*.css> 锚点（应用更新改变了结构？）');
  const inject =
    anchor[0]
    + '\n    <link rel="stylesheet" crossorigin href="./assets/' + BOOT_CSS_NAME + '">'
    + '\n    <script src="./assets/' + BOOT_JS_NAME + '" defer></script>';
  idx = idx.replace(linkRe, inject);
  const htmlTag = idx.match(/<html([^>]*)>/);
  if (!htmlTag) die('未找到 <html> 标签');
  if (!/data-zone-skin/.test(htmlTag[1])) {
    idx = idx.replace(/<html([^>]*)>/,
      '<html$1 data-zone-skin="" data-zone-colorway="zone" data-zone-canvas="auto"'
      + ' data-zone-motion="full" data-zone-dots="on">');
  }
  fs.writeFileSync(idxPath, idx);

  // ---- 4. 重打包 ----
  log('4/6', '重打包 ...');
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.rmSync(OUT + '.unpacked', { recursive: true, force: true });
  await asar.createPackageWithOptions(WORK, OUT, { unpack: '*.{node,dll,exe}' });

  // ---- 5. 校验 ----
  log('5/6', '校验 ...');
  const list = (a) => asar.listPackage(a).map((s) => s.split('\\').join('/')).sort();
  const origList = list(ORIG);
  const newList = list(OUT);
  const added = newList.filter((x) => !origList.includes(x));
  const removed = origList.filter((x) => !newList.includes(x));
  log('  ', '新增: ' + JSON.stringify(added) + '  删除: ' + JSON.stringify(removed));
  if (removed.length) die('重打包丢失了原有文件！');
  const expectedAdd = new Set([
    '/out/renderer/assets/' + BOOT_CSS_NAME,
    '/out/renderer/assets/' + BOOT_JS_NAME,
  ]);
  if (added.length !== expectedAdd.size || added.some((x) => !expectedAdd.has(x))) {
    die('新增文件不符合预期: ' + JSON.stringify(added));
  }
  const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name).split(path.sep).join('/')]);
  const origUnp = walk(ORIG + '.unpacked').map((s) => s.split('app.asar.unpacked/')[1]).sort();
  const newUnp = walk(OUT + '.unpacked').map((s) => s.split('app.asar.zone.unpacked/')[1]).sort();
  if (JSON.stringify(origUnp) !== JSON.stringify(newUnp)) {
    die('unpacked 文件列表不一致!\n  原: ' + origUnp + '\n  新: ' + newUnp);
  }
  log('  ', 'unpacked 一致 (' + newUnp.length + ' 个原生文件)');

  // ---- 6. 完成 ----
  log('6/6', '构建完成 → ' + OUT + ' (' + (fs.statSync(OUT).size / 1048576).toFixed(1) + ' MB)');
  console.log('未安装。确认无误后运行 apply.cmd（需要管理员权限写入 Program Files）。');
})().catch((e) => die(e && e.stack ? e.stack : String(e)));
