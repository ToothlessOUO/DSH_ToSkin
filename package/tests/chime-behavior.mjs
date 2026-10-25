// Behaviour checks for the completion chime: drives the forwarded api-session
// events by hand against a stub ctx/Audio, renders ZoneSettings through a
// recording createElement stub, and pins the heard/silenced cases.
import assert from 'node:assert/strict';

let entry;
globalThis.window = {
  __ModuleLoader__: { load(value) { entry = value; } },
  matchMedia: () => null,
  addEventListener() {}, removeEventListener() {},
  setTimeout: (f) => 0, clearTimeout() {},
};
await import('../client.js');

let audioPlays = 0;
let lastVolume = -1;
/* A createElement stub that records the tree; the settings test button is
   "clicked" the moment it renders so the forced play path is exercised. */
const h = (type, props, ...children) => {
  const node = { type, props: props || {}, children: children.flat() };
  if (type === 'button' && props && props.onClick && String(props.onClick).includes('playChime')) {
    props.onClick();
  }
  return node;
};
h.useState = () => [undefined, () => {}];
h.useEffect = () => {};
h.useSyncExternalStore = () => ({
  colorway: 'zone', canvas: 'auto', dots: true, motion: 'full', chime: true,
  chimeVolume: 'mid', effectiveMotion: 'full', mode: 'night', localeRevision: 0,
});

const mod = entry.factory((name) => {
  if (name === 'react') {
    return {
      createElement: h,
      useState: h.useState,
      useEffect: h.useEffect,
      useSyncExternalStore: h.useSyncExternalStore,
    };
  }
  throw new Error('unexpected require: ' + name);
});

class FakeAudio {
  constructor(src) { this.src = src; }
  play() {
    audioPlays += 1;
    lastVolume = this.volume;
    return Promise.resolve();
  }
}
globalThis.window.Audio = FakeAudio;
globalThis.Audio = FakeAudio;

const listeners = new Map();
const effects = [];
const registered = [];
const ctx = {
  theme: { getTheme: () => ({ active: { colorScheme: 'dark' } }), overrideTokens: () => () => {} },
  locale: { getLocale: () => ({ revision: 0 }), bind: () => (key) => key, register: () => () => {} },
  slots: {
    inject: (name, factory) => { factory(); return () => {}; },
    register: (spec, Component) => { registered.push({ spec, Component }); return () => {}; },
  },
  remote: {
    $on: (name, fn) => {
      if (!listeners.has(name)) listeners.set(name, []);
      listeners.get(name).push(fn);
      return () => {};
    },
  },
  effect: (fn, label) => { effects.push({ fn, label }); return () => {}; },
  on: () => () => {},
};

mod.apply(ctx, { colorway: 'zone', canvas: 'auto', motion: 'full', dots: true });
const chimeEffect = effects.find((e) => e.label.includes('task chime'));
assert.ok(chimeEffect, 'task chime effect registered');
chimeEffect.fn();

const fire = (name, ...args) => { for (const fn of listeners.get(name) || []) fn(...args); };

// A subagent child spawns: its summary carries parentSessionId.
fire('api-session/added', { sessionId: 'child-1', parentSessionId: 'root-1', origin: 'subagent' });
// Both the parent task and the child run, then both go idle.
fire('api-session/status', 'root-1', true);
fire('api-session/status', 'child-1', true);
fire('api-session/status', 'child-1', false);
assert.equal(audioPlays, 0, 'subagent finishing inside a parent task stays silent');
fire('api-session/status', 'root-1', false);
assert.equal(audioPlays, 1, 'top-level completion chimes exactly once');
assert.equal(lastVolume, 0.7, 'mid volume default applied');

// A second top-level session completing also chimes; an unseen idle does not.
fire('api-session/status', 'other-1', false);
assert.equal(audioPlays, 1, 'idle flip without a seen start never sounds');
fire('api-session/status', 'other-1', true);
fire('api-session/status', 'other-1', false);
assert.equal(audioPlays, 2, 'a second top-level completion chimes');

// The settings tree renders: the chime switch, three volume keys and the test
// button are all present (the test button was clicked during render → plays grew).
const settings = registered.find((r) => r.spec.name === 'settings.general.item');
assert.ok(settings, 'settings component registered');
const settingsNode = settings.Component({});
assert.ok(settingsNode, 'settings block renders');
const buttons = [];
const walk = (node) => {
  if (node && node.type === 'button') buttons.push(node);
  for (const child of (node && node.children) || []) walk(child);
};
walk(settingsNode);
const switchBtn = buttons.find((b) => b.props.role === 'switch'
  && b.props['aria-checked'] === true && String(b.props.onClick).includes('chime'));
assert.ok(switchBtn, 'chime switch rendered on');
const volumeBtns = buttons.filter((b) => String(b.props.onClick).includes('chimeVolume'));
assert.equal(volumeBtns.length, 3, 'three volume steps rendered');
const testBtn = buttons.find((b) => b.children && b.children.some((c) => c === 'chime.test'));
assert.ok(testBtn, 'chime test button rendered');
assert.equal(audioPlays, 3, 'test button forces a play even mid-suite');

console.log('chime harness passed: plays=' + audioPlays + ', volume=' + lastVolume + ', buttons=' + buttons.length);
