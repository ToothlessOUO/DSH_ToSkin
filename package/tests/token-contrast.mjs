// Pure-helper checks for the ZONE skin: token completeness and contrast.
import assert from 'node:assert/strict';

let entry;
globalThis.window = { __ModuleLoader__: { load(value) { entry = value; } } };
await import('../client.js');

assert.ok(entry && entry.id === '@local/dsh-zone-skin', 'module registers its package id');
const reactStub = {
  createElement: () => null,
  useState: () => [undefined, () => {}],
  useEffect: () => {},
  useSyncExternalStore: () => undefined,
};
const mod = entry.factory(() => reactStub);
assert.equal(typeof mod.apply, 'function', 'factory returns apply');

function channel(value) {
  const n = value / 255;
  return n <= 0.03928 ? n / 12.92 : Math.pow((n + 0.055) / 1.055, 2.4);
}

function toRgb(color) {
  const hex = /^#([0-9a-f]{6})$/i.exec(color);
  if (hex) {
    const raw = hex[1];
    return [0, 2, 4].map((i) => parseInt(raw.slice(i, i + 2), 16));
  }
  const rgba = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i.exec(color);
  if (rgba) return [Number(rgba[1]), Number(rgba[2]), Number(rgba[3])];
  throw new Error('unparsable color: ' + color);
}

function contrast(a, b) {
  const [l1, l2] = [a, b]
    .map((color) => toRgb(color).map(channel))
    .map(([r, g, b]) => 0.2126 * r + 0.7152 * g + 0.0722 * b)
    .sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}

const COLORWAYS = ['zone', 'ember', 'hazard', 'cobalt'];
const CANVASES = ['auto', 'day', 'night'];
const modeFor = { auto: 'light', day: 'light', night: 'dark' };
const COLOR = /^(#[0-9a-f]{6}|rgba?\([\d ,.]+\)|transparent|none)$/i;
const SHADOW = /^\d.*px .*rgba?\(/;

let tokens = 0;
let pairs = 0;
for (const colorway of COLORWAYS) {
  for (const canvas of CANVASES) {
    const layer = mod.tokensFor({ colorway, canvas, motion: 'full', dots: true });
    const names = Object.keys(layer);
    assert.ok(names.length > 65, `${colorway}/${canvas} exposes a full layer (${names.length})`);
    for (const name of names) {
      const value = layer[name];
      assert.equal(typeof value, 'object', `${name} is a modes pair`);
      for (const mode of ['light', 'dark']) {
        assert.equal(typeof value[mode], 'string', `${name}.${mode} is a string`);
        assert.ok(!/undefined|NaN|\[object/.test(value[mode]), `${name}.${mode} is clean: ${value[mode]}`);
        if ((name.startsWith('--dsw-elevation-') && !name.endsWith('-stroke-color')) || name === '--dsw-shadow-lv3') {
          assert.match(value[mode], SHADOW, `${name}.${mode} is a shadow: ${value[mode]}`);
        } else if (name.startsWith('--dsw-alias-') || name.startsWith('--dsw-specific-') || name.startsWith('--dsh-scrollbar-thumb')) {
          assert.match(value[mode], COLOR, `${name}.${mode} looks like CSS: ${value[mode]}`);
        }
        tokens += 1;
      }
    }

    const mode = modeFor[canvas];
    const at = (name) => layer[name][mode];
    const checks = [
      ['label-primary on bg-base', at('--dsw-alias-label-primary'), at('--dsw-alias-bg-base'), 7],
      ['label-secondary on bg-base', at('--dsw-alias-label-secondary'), at('--dsw-alias-bg-base'), 4.5],
      ['label-tertiary on bg-base', at('--dsw-alias-label-tertiary'), at('--dsw-alias-bg-base'), 4.5],
      ['label-primary on bg-layer-1', at('--dsw-alias-label-primary'), at('--dsw-alias-bg-layer-1'), 7],
      ['label-primary on bg-layer-2', at('--dsw-alias-label-primary'), at('--dsw-alias-bg-layer-2'), 7],
      ['label-primary on menu surface', at('--dsw-alias-label-primary'), at('--dsw-alias-menu-surface-fill'), 7],
      ['primary button text', at('--dsw-alias-label-primary-foreground'), at('--dsw-alias-button-primary-fill'), 4.5],
      ['toast text', at('--dsw-alias-toast-label'), at('--dsw-alias-toast-bg'), 4.5],
      /* The chat plate always carries white ink (the owner's choice), so its pair
         is not scored here; the block below pins the fill/ink relationship. */
      ['tooltip text (static near-white)', '#f4efe3', at('--dsw-alias-tooltip-bg'), 4.5],
      ['warn badge text', at('--dsw-alias-state-warn-label'), at('--dsw-alias-state-warn-tertiary'), 3],
      ['success badge text', at('--dsw-alias-state-success-primary'), at('--dsw-alias-state-success-tertiary'), 3],
      ['link on bg-base', at('--dsw-alias-link'), at('--dsw-alias-bg-base'), 3],
    ];
    for (const [label, foreground, background, minimum] of checks) {
      const ratio = contrast(foreground, background);
      assert.ok(ratio >= minimum, `${colorway}/${canvas} ${label}: ${ratio.toFixed(2)} < ${minimum} (${foreground} on ${background})`);
      pairs += 1;
    }
  }
}

// The chat plate is the colorway accent — the same fill a selected session row
// takes — in every colorway and both canvases, and its ink is always white, the
// same voice the accent-filled rows and buttons use. This is a deliberate choice
// for the two bright night accents (zone orange, hazard yellow), where white is
// below the usual 3:1 floor; the assertion keeps a future "readability fix" from
// silently reintroducing a second ink colour.
for (const colorway of COLORWAYS) {
  for (const canvas of CANVASES) {
    const layer = mod.tokensFor({ colorway, canvas, motion: 'full', dots: true });
    const mode = modeFor[canvas];
    const plate = layer['--dsw-specific-bubble'][mode];
    assert.equal(plate, layer['--dsw-alias-brand-primary'][mode], `${colorway}/${canvas}: plate is the accent`);
    assert.equal(layer['--zone-plate-ink'][mode], '#ffffff', `${colorway}/${canvas}: plate ink is white`);
  }
}

// Preference normalization keeps unknown input usable.
assert.deepEqual(
  mod.normalizePrefs({ colorway: 'lime', canvas: 'dusk', motion: 'warp', dots: 'yes' }),
  { colorway: 'zone', canvas: 'auto', motion: 'full', dots: true, chime: true, chimeVolume: 'mid' },
);
assert.deepEqual(
  mod.normalizePrefs({ colorway: 'hazard', canvas: 'night', motion: 'off', dots: false }),
  { colorway: 'hazard', canvas: 'night', motion: 'off', dots: false, chime: true, chimeVolume: 'mid' },
);
// Chime preferences survive normalization; an unknown volume falls back to mid.
assert.deepEqual(
  mod.normalizePrefs({ chime: false, chimeVolume: 'high' }),
  { colorway: 'zone', canvas: 'auto', motion: 'full', dots: true, chime: false, chimeVolume: 'high' },
);
assert.equal(mod.normalizePrefs({ chimeVolume: 'loud' }).chimeVolume, 'mid');
assert.equal(mod.nextCanvas('auto'), 'day');
assert.equal(mod.nextCanvas('day'), 'night');
assert.equal(mod.nextCanvas('night'), 'auto');
assert.equal(mod.nextColorway('zone'), 'ember');
assert.equal(mod.nextColorway('hazard'), 'cobalt');
assert.equal(mod.nextColorway('cobalt'), 'zone');

// Forcing a canvas collapses both mode entries to that canvas.
const forced = mod.tokensFor({ colorway: 'ember', canvas: 'night', motion: 'full', dots: true });
assert.equal(forced['--dsw-alias-bg-base'].light, forced['--dsw-alias-bg-base'].dark, 'forced night maps both modes');

// Brand ink flips with the colorway, not with taste.
assert.equal(mod.bestOn('#ff6f1a'), '#14110d');
assert.equal(mod.bestOn('#a8770a'), '#14110d');
assert.equal(mod.bestOn('#7a2f12'), '#f4efe3');

console.log(`tokens checked: ${tokens}; contrast pairs: ${pairs}; colorways: ${COLORWAYS.length}`);
console.log('zone skin helper checks passed');
