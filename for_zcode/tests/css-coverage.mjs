/* Stylesheet coverage test for the ZONE skin on ZCode.
 *
 * Ported from the DSH original tests/css-coverage.mjs:
 *   1. zone.css braces balance and every rule has a selector;
 *   2. every .zone-* class zone-boot.js renders has a rule in zone.css;
 *   3. every var() the stylesheet references resolves — either the app
 *      publishes that token (tests/app-token-names.json, extracted from the
 *      installed styles-*.css) or zone.css defines it. An unresolved var()
 *      makes the declaration invalid at computed-value time and it is
 *      *silently dropped* — the exact failure mode NOTES.md warns about.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(HERE, '..');
const CSS = fs.readFileSync(path.join(ROOT, 'zone.css'), 'utf8');
const BOOT = fs.readFileSync(path.join(ROOT, 'zone-boot.js'), 'utf8');
const APP_TOKENS = new Set(JSON.parse(fs.readFileSync(path.join(HERE, 'app-token-names.json'), 'utf8')));

let failures = 0;
function ok(condition, message) {
  if (condition) console.log('  ok  ' + message);
  else { failures++; console.error('  FAIL ' + message); }
}

/* ---------------------------------------------------------- structure */

console.log('stylesheet structure');
{
  let depth = 0;
  let line = 1;
  let balanced = true;
  for (const ch of CSS) {
    if (ch === '\n') line++;
    if (ch === '{') depth++;
    if (ch === '}') {
      depth--;
      if (depth < 0) { balanced = false; console.error(`  stray } at line ${line}`); break; }
    }
  }
  ok(balanced && depth === 0, `braces balance (final depth ${depth})`);

  const commentless = CSS.replace(/\/\*[\s\S]*?\*\//g, '');
  const rules = commentless.split('}').filter((r) => r.trim().length);
  let selectorless = 0;
  for (const rule of rules) {
    const head = rule.split('{')[0].trim();
    if (!head) selectorless++;
  }
  ok(selectorless === 0, 'every rule carries a selector');
}

/* -------------------------------------------------- boot classes styled */

console.log('every boot-rendered class is styled');
{
  const rendered = new Set();
  for (const m of BOOT.matchAll(/['"`]((?:zone-[a-z][a-z0-9-]*(?:\s+)?)+)['"`]/g)) {
    for (const name of m[1].trim().split(/\s+/)) {
      const clean = name.replace(/[^a-z0-9]+$/, '');
      if (/^zone-[a-z]/.test(clean)) rendered.add(clean);
    }
  }
  const styled = new Set();
  for (const m of CSS.matchAll(/\.((?:zone-)[a-z0-9-]+)/g)) styled.add(m[1]);
  const missing = [...rendered].filter((name) => !styled.has(name));
  ok(rendered.size > 10, `boot renders ${rendered.size} zone-* classes`);
  ok(missing.length === 0, `all styled (missing: ${JSON.stringify(missing)})`);
}

/* --------------------------------------------------- var() resolution */

console.log('every var() reference resolves');
{
  const definedInSkin = new Set();
  for (const m of CSS.matchAll(/(--[a-zA-Z0-9-]+)\s*:/g)) definedInSkin.add(m[1]);
  const writtenByBoot = new Set();
  for (const m of BOOT.matchAll(/'(--zone-[a-z0-9-]+)'/g)) writtenByBoot.add(m[1]);

  const referenced = new Set();
  for (const m of CSS.matchAll(/var\(\s*(--[a-zA-Z0-9-]+)/g)) referenced.add(m[1]);

  const unresolved = [...referenced].filter((name) =>
    !definedInSkin.has(name) && !APP_TOKENS.has(name) && !writtenByBoot.has(name));
  ok(unresolved.length === 0,
    'all referenced tokens are published by the app, the skin, or the boot script'
    + (unresolved.length ? ` (unresolved: ${JSON.stringify(unresolved)})` : ''));

  /* every app token the skin overrides must actually exist in the app —
     a typo there silently restyles nothing. --color-ring is the one
     deliberate exception: the app's ring-ring/* utilities reference it
     without ever defining it, so those declarations are dropped today;
     the skin defines it to light the brand focus ring. */
  const DELIBERATE = new Set(['--color-ring']);
  const overridden = new Set();
  const ruleRe = /([^{}]+)\{([^{}]*)\}/g;
  let m;
  while ((m = ruleRe.exec(CSS))) {
    if (!m[1].includes('data-zone-skin')) continue;
    for (const v of m[2].matchAll(/(--(?:color|font|radius|highspeed|animated|ui-font|lucide)-?[a-zA-Z0-9-]*)\s*:/g)) {
      overridden.add(v[1]);
    }
  }
  const unknown = [...overridden].filter((name) => !APP_TOKENS.has(name) && !DELIBERATE.has(name));
  ok(unknown.length === 0,
    'every overridden app token exists in the installed styles-*.css'
    + (unknown.length ? ` (unknown: ${JSON.stringify(unknown)})` : ''));
}

/* ------------------------------------------------------ boot syntax */

console.log('boot script');
ok(BOOT.includes("window.__zoneSkinBooted"), 'boot guards against double-injection');
ok(!/\bTODO\b/.test(CSS + BOOT), 'no TODOs left in the skin');

if (failures) {
  console.error(`\n${failures} failure(s)`);
  process.exit(1);
}
console.log('\nstylesheet coverage ok');
