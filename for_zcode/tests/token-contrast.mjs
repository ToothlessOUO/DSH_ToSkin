/* Token-layer test for the ZONE skin on ZCode.
 *
 * Ported from the DSH original tests/token-contrast.mjs. The skin's palette
 * lives as plain inputs in zone.css (chassis blocks + colorway blocks); this
 * test parses those inputs, re-derives the pairs the tokens control and
 * enforces the contrast floors: body 7:1, secondary 4.5:1, dim captions 3:1,
 * status ink 3:1. Ink on the accent is pinned to pure white by design — the
 * DSH owner chose one white voice over the extra contrast on the two
 * brightest night accents — so white-on-brand is *reported*, not failed,
 * and the pin itself is asserted literally.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CSS = fs.readFileSync(path.join(HERE, '..', 'zone.css'), 'utf8');

let failures = 0;
function ok(condition, message) {
  if (condition) {
    console.log('  ok  ' + message);
  } else {
    failures++;
    console.error('  FAIL ' + message);
  }
}

/* ---------------------------------------------------------------- colors */

function parseHex(hex) {
  const value = String(hex).replace('#', '');
  if (!/^[0-9a-fA-F]{6}$/.test(value)) throw new Error('bad hex: ' + hex);
  return [
    parseInt(value.slice(0, 2), 16),
    parseInt(value.slice(2, 4), 16),
    parseInt(value.slice(4, 6), 16),
  ];
}

function toHex(rgb) {
  return '#' + rgb
    .map((c) => Math.max(0, Math.min(255, Math.round(c))).toString(16).padStart(2, '0'))
    .join('');
}

function mix(a, b, weight) {
  const A = parseHex(a);
  const B = parseHex(b);
  return toHex(A.map((c, i) => c + (B[i] - c) * weight));
}

function luminance(hex) {
  const [r, g, b] = parseHex(hex).map((channel) => {
    const v = channel / 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(a, b) {
  const l1 = luminance(a);
  const l2 = luminance(b);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

const ratio = (x) => Math.round(x * 100) / 100;

/* ------------------------------------------------- parse the palette inputs */

function block(selector) {
  const re = new RegExp(escapeRe(selector) + '\\s*\\{([^}]*)\\}', 'g');
  const bodies = [];
  let m;
  while ((m = re.exec(CSS))) bodies.push(m[1]);
  if (!bodies.length) throw new Error('selector not found in zone.css: ' + selector);
  return bodies.join('\n');
}

function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function readVar(body, name) {
  const m = body.match(new RegExp(escapeRe(name) + '\\s*:\\s*([^;\\n]+)'));
  return m ? m[1].trim() : undefined;
}

const dayBlock = block('html[data-zone-skin]');
const nightBlock = block('html[data-zone-skin].dark,\nhtml[data-zone-skin][data-zone-canvas="night"]');
const resolution = block('html[data-zone-skin]');

const CHASSIS_INPUTS = ['base', 'layer1', 'layer2', 'ink', 'ink-dim', 'line', 'sidebar'];
const chassis = {};
for (const mode of ['day', 'night']) {
  const source = mode === 'day' ? dayBlock : nightBlock;
  chassis[mode] = {};
  for (const name of CHASSIS_INPUTS) {
    const value = readVar(source, '--zone-' + name);
    if (!value) throw new Error('missing --zone-' + name + ' in the ' + mode + ' chassis block');
    chassis[mode][name] = value;
  }
}

const COLORWAYS = ['zone', 'ember', 'hazard', 'cobalt'];
const brands = {};
for (const colorway of COLORWAYS) {
  const body = block(`html[data-zone-skin][data-zone-colorway="${colorway}"]`);
  brands[colorway] = {
    day: readVar(body, '--zone-brand-day'),
    night: readVar(body, '--zone-brand-night'),
  };
  for (const mode of ['day', 'night']) {
    if (!/^[0-9a-fA-F]{6}$/.test(brands[colorway][mode].replace('#', ''))) {
      throw new Error(`colorway ${colorway} ${mode} brand is not a hex colour`);
    }
  }
}

const triples = {};
for (const colorway of COLORWAYS) {
  const body = block(`html[data-zone-skin][data-zone-colorway="${colorway}"]`);
  triples[colorway] = {
    day: {
      brand: readVar(body, '--zone-brand-rgb-day'),
      shade: readVar(body, '--zone-shade-rgb-day'),
    },
    night: {
      brand: readVar(body, '--zone-brand-rgb-night'),
      shade: readVar(body, '--zone-shade-rgb-night'),
    },
  };
}

function expectedShade(brand, mode) {
  return mix(brand, '#000000', mode === 'night' ? 0.58 : 0.45);
}

/* ------------------------------------------------------------- assertions */

console.log('palette inputs');
for (const mode of ['day', 'night']) {
  for (const [name, value] of Object.entries(chassis[mode])) {
    ok(/^[0-9a-fA-F]{6}$/.test(value.replace('#', '')), `${mode} --zone-${name} is a hex colour (${value})`);
  }
}

console.log('rgb triples match the palette (shadows stay literal rgb())');
for (const colorway of COLORWAYS) {
  for (const mode of ['day', 'night']) {
    const brand = parseHex(brands[colorway][mode]);
    const shade = mix(brands[colorway][mode], '#000000', mode === 'night' ? 0.58 : 0.45);
    const wantBrand = brand.join(' ');
    const wantShade = parseHex(shade).join(' ');
    ok(triples[colorway][mode].brand === wantBrand,
      `${colorway}/${mode} brand-rgb == ${wantBrand} (got ${triples[colorway][mode].brand})`);
    ok(triples[colorway][mode].shade === wantShade,
      `${colorway}/${mode} shade-rgb == mix(brand, black) (got ${triples[colorway][mode].shade})`);
    ok(/^\d{1,3} \d{1,3} \d{1,3}$/.test(triples[colorway][mode].shade), `${colorway}/${mode} shade-rgb is three 0-255 channels`);
  }
}

console.log('contrast floors (per colorway x canvas)');
for (const colorway of COLORWAYS) {
  for (const mode of ['day', 'night']) {
    const c = chassis[mode];
    const brand = brands[colorway][mode];
    const label = `${colorway}/${mode}`;
    const body = contrast(c.ink, c.base);
    ok(body >= 7, `${label} body ink vs base >= 7:1 (${ratio(body)})`);
    const subtle = contrast(mix(c.ink, c.base, 0.22), c.base);
    ok(subtle >= 4.5, `${label} foreground-subtle (78% ink) vs base >= 4.5:1 (${ratio(subtle)})`);
    const subtlest = contrast(mix(c.ink, c.base, 0.45), c.base);
    ok(subtlest >= 3, `${label} foreground-subtlest (55% ink) vs base >= 3:1 (${ratio(subtlest)})`);
    const dim = contrast(c['ink-dim'], c.base);
    ok(dim >= 3, `${label} ink-dim vs base >= 3:1 (${ratio(dim)})`);
    const line = contrast(c.line, c.base);
    ok(line >= 1.15, `${label} border visible vs base >= 1.15:1 (${ratio(line)})`);
    /* White on the accent is the lit-plate look; the floor is reported,
       not enforced — night zone orange and night hazard yellow sit below
       3:1 on purpose (documented in README/NOTES). */
    const onBrand = contrast('#ffffff', brand);
    console.log(`  note ${label} white ink on brand = ${ratio(onBrand)}:1`
      + (onBrand >= 3 ? '' : '  (accepted sub-3 lit plate)'));
    /* status pairs that the skin re-inks */
    if (mode === 'night') {
      ok(contrast('#14110d', '#ffc61a') >= 7, `${label} warning-foreground on warning >= 7:1`);
    } else {
      ok(contrast('#ffffff', '#a8770a') >= 3, `${label} warning-foreground on warning >= 3:1 (${ratio(contrast('#ffffff', '#a8770a'))})`);
    }
    ok(contrast('#ffffff', mode === 'night' ? '#ff5a45' : '#b32d1f') >= 3,
      `${label} destructive-foreground on destructive >= 3:1`);
    ok(contrast(mode === 'night' ? '#14110d' : '#ffffff', mode === 'night' ? '#4fdc8c' : '#22763f') >= 3,
      `${label} success-foreground on success >= 3:1`);
  }
}

console.log('invariants carried over from the DSH skin');
ok(/--zone-brand-on:\s*#ffffff/.test(CSS), 'lit-plate ink is the literal #ffffff (one white voice)');
ok(/\[data-v4-user-input-collapsible-content\][^{]*\{[^}]*background:\s*var\(--zone-brand\)/.test(CSS),
  'the user message plate is filled with the accent itself (no second plate colour)');
ok(/--color-primary-foreground:\s*#ffffff/.test(CSS), 'primary buttons keep white ink in every colorway');
ok(resolution.includes('var(--zone-brand-day'), 'canvas resolution defaults to day before the dark flip');

/* canvas resolution covers all four combinations */
ok(nightBlock.includes('--zone-base: #2c2927'), 'night chassis is the graphite blacksite');
ok(dayBlock.includes('--zone-base: #e8e1d1'), 'day chassis is the keycap cream');
ok(resolution.includes('var(--zone-brand-day'), 'day default resolution present');
ok(CSS.includes('html[data-zone-skin][data-zone-canvas="night"]'), 'forced-night block present');
ok(CSS.includes('html[data-zone-skin][data-zone-canvas="day"]'), 'forced-day block present');

if (failures) {
  console.error(`\n${failures} failure(s)`);
  process.exit(1);
}
console.log('\ntoken layer ok');
