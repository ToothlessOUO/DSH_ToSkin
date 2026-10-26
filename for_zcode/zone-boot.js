/* ZONE skin for ZCode — client half (R1).
 *
 * Injected into the renderer by tools/build.js as a plain <script defer>.
 * ZCode has no plugin slots, so everything the DSH original did through
 * React components and ctx.theme.overrideTokens() happens here against the
 * live document, outside #root (React never rewrites what it does not own):
 *
 *   - preferences in localStorage, normalised + multi-window synced
 *   - the html[data-zone-*] attributes zone.css reads
 *   - the 24px SVG cursor set, published as --zone-cursor* variables
 *   - the atmosphere layer: cast shadow, halftone screen, pointer lens,
 *     four taped corner brackets
 *   - the console: a collapsed chip docked bottom-left that opens a panel
 *     with the colorway / canvas / motion / dots controls, the cream sticker
 *     and the LED device bar
 *   - the opt-in DOM probe (localStorage['zcode-zone-skin:probe'] = '1')
 *
 * No dependencies, no framework. Keyboard: Ctrl+Alt+Z colorway,
 * Ctrl+Alt+X canvas, Ctrl+Alt+H toggle the console.
 */
(() => {
  'use strict';

  if (window.__zoneSkinBooted) return;
  window.__zoneSkinBooted = true;

  const REV = 'R1';
  const PREF_KEY = 'zcode-zone-skin:prefs';
  const PROBE_FLAG = 'zcode-zone-skin:probe';
  const PROBE_KEY = 'zcode-zone-skin:diag';

  const COLORWAY_ORDER = ['zone', 'ember', 'hazard', 'cobalt'];
  const CANVAS_ORDER = ['auto', 'day', 'night'];
  const MOTION_ORDER = ['full', 'quiet', 'off'];
  const CONSOLE_ORDER = ['visible', 'hidden'];

  const COLORWAY_LABEL = {
    zone: { en: 'Zone orange', zh: 'ZONE 橙' },
    ember: { en: 'Ember', zh: '余烬红' },
    hazard: { en: 'Hazard', zh: '警戒黄' },
    cobalt: { en: 'Cobalt', zh: '钴蓝' },
  };

  /* ------------------------------------------------------------ palettes */

  const COLORWAYS = {
    zone: { night: '#ff6f1a', day: '#e2560d' },
    ember: { night: '#ff4632', day: '#c62c1b' },
    hazard: { night: '#ffc61a', day: '#a8770a' },
    cobalt: { night: '#4d94ff', day: '#1f5fd6' },
  };

  const brandOf = (colorway, mode) => COLORWAYS[colorway][mode];

  /* ------------------------------------------------------------- cursors */

  const CURSOR_CREAM = '#f8f3e8';
  const CURSOR_GRAPHITE = '#2c2927';

  function cursorImage(body) {
    const svg = "<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'>"
      + body + '</svg>';
    const encoded = svg.replaceAll('<', '%3C').replaceAll('>', '%3E').replaceAll('#', '%23');
    return 'url("data:image/svg+xml,' + encoded + '")';
  }

  /** Haloed line art: cream keeps it visible on graphite, the colorway core on cream. */
  function cursorGlyph(brand, paths) {
    const halo = "<g stroke='" + CURSOR_CREAM + "' stroke-width='4.2' stroke-linecap='round'"
      + " stroke-linejoin='round' fill='none'>" + paths + '</g>';
    const core = "<g stroke='" + brand + "' stroke-width='1.8' stroke-linecap='round'"
      + " stroke-linejoin='round' fill='none'>" + paths + '</g>';
    return halo + core;
  }

  /** One cursor set per colorway/canvas. wait/progress/help/crosshair/
   *  grabbing/move stay native: CSS cursor images cannot animate. */
  function cursorSet(colorway, mode) {
    const brand = brandOf(colorway, mode);
    const arrow = 'M4 2.2 L4 19.0 L9.0 14.4 L17.0 13.2 Z';
    return {
      '--zone-cursor': cursorImage("<path d='" + arrow + "' fill='" + CURSOR_GRAPHITE
        + "' stroke='" + brand + "' stroke-width='1.6' stroke-linejoin='miter' stroke-miterlimit='4'/>")
        + ' 4 2, default',
      '--zone-cursor-text': cursorImage(cursorGlyph(brand,
        "<path d='M12 4.8 V19.2'/><path d='M8.8 4.8 H15.2'/><path d='M8.8 19.2 H15.2'/>")) + ' 12 5, text',
      '--zone-cursor-pointer': cursorImage("<path d='M8.4 6.8 L8.4 20.2 L12.4 16.6 L18.8 15.6 Z' fill='"
        + CURSOR_GRAPHITE + "' stroke='" + brand + "' stroke-width='1.5'"
        + " stroke-linejoin='miter' stroke-miterlimit='4'/>"
        + "<g stroke='" + brand + "' stroke-width='2.2' stroke-linecap='round' fill='none'>"
        + "<path d='M2.6 4.2 H7.8'/><path d='M5.2 1.6 V6.8'/></g>") + ' 8 7, pointer',
      '--zone-cursor-not-allowed': cursorImage(cursorGlyph(brand,
        "<circle cx='12' cy='12' r='7.4'/><path d='M7.2 7.2 L16.8 16.8'/>")) + ' 12 12, not-allowed',
    };
  }

  const CURSOR_VARS = ['--zone-cursor', '--zone-cursor-text', '--zone-cursor-pointer', '--zone-cursor-not-allowed'];

  /* ---------------------------------------------------------------- prefs */

  function normalizePrefs(input) {
    const raw = input && typeof input === 'object' ? input : {};
    return {
      colorway: COLORWAY_ORDER.includes(raw.colorway) ? raw.colorway : 'zone',
      canvas: CANVAS_ORDER.includes(raw.canvas) ? raw.canvas : 'auto',
      motion: MOTION_ORDER.includes(raw.motion) ? raw.motion : 'full',
      dots: raw.dots !== false,
      console: CONSOLE_ORDER.includes(raw.console) ? raw.console : 'visible',
    };
  }

  function readStored() {
    try {
      const raw = window.localStorage.getItem(PREF_KEY);
      if (!raw) return undefined;
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === 'object' ? parsed : undefined;
    } catch {
      return undefined;
    }
  }

  function writeStored(prefs) {
    try {
      window.localStorage.setItem(PREF_KEY, JSON.stringify(prefs));
    } catch {
      /* private mode can refuse storage; the session keeps working */
    }
  }

  const step = (order, value) => order[(order.indexOf(value) + 1) % order.length];

  /* ---------------------------------------------------------------- state */

  const reduce = typeof window.matchMedia === 'function'
    ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  let prefs = normalizePrefs(readStored());
  let systemNight = document.documentElement.classList.contains('dark');

  const modeOf = () => (prefs.canvas === 'auto' ? (systemNight ? 'night' : 'day') : prefs.canvas);
  const effectiveMotion = () => (reduce && reduce.matches ? 'off' : prefs.motion);

  const listeners = new Set();
  const subscribe = (fn) => { listeners.add(fn); return () => listeners.delete(fn); };
  const publish = () => { for (const fn of [...listeners]) fn(); };

  function applyRoot() {
    const root = document.documentElement;
    const mode = modeOf();
    root.setAttribute('data-zone-skin', '');
    root.setAttribute('data-zone-colorway', prefs.colorway);
    root.setAttribute('data-zone-canvas', prefs.canvas);
    root.setAttribute('data-zone-motion', effectiveMotion());
    root.setAttribute('data-zone-dots', prefs.dots ? 'on' : 'off');
    const set = cursorSet(prefs.colorway, mode);
    for (const name of CURSOR_VARS) root.style.setProperty(name, set[name]);
  }

  function update(patch) {
    const next = normalizePrefs({ ...prefs, ...patch });
    if (JSON.stringify(next) === JSON.stringify(prefs)) return;
    prefs = next;
    writeStored(prefs);
    applyRoot();
    renderConsole();
    publish();
  }

  /* The app flips theme classes on <html> at runtime; auto-canvas follows. */
  const themeObserver = new MutationObserver(() => {
    const night = document.documentElement.classList.contains('dark');
    if (night !== systemNight) {
      systemNight = night;
      applyRoot();
      renderConsole();
      publish();
    }
  });
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });

  if (reduce) reduce.addEventListener('change', () => { applyRoot(); publish(); });

  window.addEventListener('storage', (event) => {
    if (event.key !== PREF_KEY && event.key !== null) return;
    const next = normalizePrefs(readStored());
    if (JSON.stringify(next) === JSON.stringify(prefs)) return;
    prefs = next;
    applyRoot();
    renderConsole();
    publish();
  });

  window.addEventListener('keydown', (event) => {
    if (!(event.ctrlKey && event.altKey) || event.shiftKey || event.metaKey) return;
    const tag = (event.target && event.target.tagName) || '';
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(tag)) return;
    const key = event.key.toLowerCase();
    if (key === 'z') { update({ colorway: step(COLORWAY_ORDER, prefs.colorway) }); event.preventDefault(); }
    else if (key === 'x') { update({ canvas: step(CANVAS_ORDER, prefs.canvas) }); event.preventDefault(); }
    else if (key === 'h') { update({ console: prefs.console === 'visible' ? 'hidden' : 'visible' }); event.preventDefault(); }
  });

  /* ------------------------------------------------------------ dom build */

  const el = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  };

  let consoleRoot = null;
  let chipSwatch = null;
  let chipLabel = null;
  let panel = null;

  function buildConsole() {
    consoleRoot = el('div', 'zone-console');
    consoleRoot.setAttribute('role', 'group');
    consoleRoot.setAttribute('aria-label', 'ZONE skin');

    const chip = el('button', 'zone-chip');
    chip.type = 'button';
    chip.title = 'ZONE skin — click to open, Ctrl+Alt+H to hide';
    chipSwatch = el('span', 'zone-dot');
    chipLabel = el('span', null, 'ZONE');
    chip.append(chipSwatch, chipLabel);
    chip.addEventListener('click', () => {
      panel.hidden = !panel.hidden;
    });
    consoleRoot.appendChild(chip);

    panel = el('div', 'zone-panel');
    panel.hidden = true;

    panel.appendChild(buildSticker());

    const rows = el('div', 'zone-rows');
    rows.appendChild(buildRow('Colorway', 'colorway-row', COLORWAY_ORDER, (key) => ({
      node: el('span', 'zone-dot'),
      swatch: brandOf(key, modeOf()),
      label: COLORWAY_LABEL[key].en,
    }), (key) => update({ colorway: key }), () => prefs.colorway));
    rows.appendChild(buildRow('Canvas', 'canvas-row', CANVAS_ORDER, (key) => ({
      node: null,
      label: key === 'auto' ? 'Follow app' : key === 'day' ? 'Cream' : 'Blacksite',
    }), (key) => update({ canvas: key }), () => prefs.canvas));
    rows.appendChild(buildRow('Motion', 'motion-row', MOTION_ORDER, (key) => ({
      node: null,
      label: key === 'full' ? 'Full' : key === 'quiet' ? 'Quiet' : 'Off',
    }), (key) => update({ motion: key }), () => prefs.motion));
    rows.appendChild(buildSwitchRow());
    panel.appendChild(rows);

    panel.appendChild(buildDeviceBar());

    consoleRoot.appendChild(panel);
    (document.body || document.documentElement).appendChild(consoleRoot);
  }

  function buildSticker() {
    const sticker = el('div', 'zone-sticker');
    sticker.setAttribute('aria-hidden', 'true');
    sticker.appendChild(el('span', 'zone-sticker-mark', 'ZONE'));
    sticker.appendChild(el('span', 'zone-sticker-tape'));
    const chips = el('span', 'zone-sticker-chips');
    for (const key of COLORWAY_ORDER) {
      const chip = el('span', 'zone-sticker-chip');
      chip.style.setProperty('--zone-swatch', brandOf(key, modeOf()));
      chips.appendChild(chip);
    }
    sticker.appendChild(chips);
    sticker.appendChild(el('span', 'zone-sticker-code', 'Skin / 01'));
    return sticker;
  }

  const rowRefs = [];

  function buildRow(labelText, rowClass, keys, describe, onPick, getActive) {
    const field = el('div', 'zone-field');
    field.appendChild(el('span', 'zone-field-label', labelText));
    const row = el('div', 'zone-row ' + rowClass);
    row.setAttribute('role', 'group');
    row.setAttribute('aria-label', labelText);
    const refs = { row, keys, describe, onPick, getActive, buttons: new Map() };
    rowRefs.push(refs);
    field.appendChild(row);
    return field;
  }

  function renderRow(refs) {
    const mode = modeOf();
    for (const key of refs.keys) {
      let button = refs.buttons.get(key);
      const info = refs.describe(key);
      if (!button) {
        button = el('button', 'zone-btn');
        button.type = 'button';
        if (info.node) button.appendChild(info.node);
        button.appendChild(document.createTextNode(''));
        button.addEventListener('click', () => refs.onPick(key));
        refs.row.appendChild(button);
        refs.buttons.set(key, button);
      }
      const textNode = button.lastChild;
      textNode.textContent = info.label;
      const swatchHolder = button.querySelector('.zone-dot');
      if (swatchHolder) {
        const swatch = info.swatch !== undefined ? info.swatch : brandOf(key, mode);
        swatchHolder.style.setProperty('--zone-swatch', swatch);
      }
      const active = refs.getActive() === key;
      if (active) button.setAttribute('aria-pressed', 'true');
      else button.removeAttribute('aria-pressed');
    }
  }

  function buildSwitchRow() {
    const field = el('div', 'zone-field');
    field.appendChild(el('span', 'zone-field-label', 'Halftone'));
    const switchButton = el('button', 'zone-switch');
    switchButton.type = 'button';
    switchButton.setAttribute('role', 'switch');
    switchButton.setAttribute('aria-label', 'Halftone texture');
    switchButton.appendChild(el('span', 'zone-toggle-track'));
    switchButton.setAttribute('aria-checked', String(prefs.dots));
    switchButton.addEventListener('click', () => update({ dots: !prefs.dots }));
    field.appendChild(switchButton);
    rowRefs.push({ switchButton });
    return field;
  }

  function buildDeviceBar() {
    const bar = el('div', 'zone-bar');
    bar.setAttribute('aria-hidden', 'true');
    const live = el('span', 'zone-live');
    live.appendChild(el('span', 'zone-led'));
    live.appendChild(document.createTextNode('Live'));
    bar.appendChild(live);
    bar.appendChild(el('span', 'zone-tape'));
    bar.appendChild(el('span', 'zone-id', 'ZONE/01 ' + REV));
    bar.appendChild(el('span', 'zone-sheet', sheetId()));
    return bar;
  }

  function sheetId() {
    const title = String(document.title || '').trim();
    const cleaned = title === 'ZCode' || title === '' ? '' : title;
    const id = cleaned.slice(0, 6).toUpperCase();
    return id || '------';
  }

  function renderConsole() {
    if (!consoleRoot) return;
    consoleRoot.hidden = prefs.console === 'hidden';
    if (consoleRoot.hidden) return;
    const mode = modeOf();
    chipSwatch.style.setProperty('--zone-swatch', brandOf(prefs.colorway, mode));
    chipLabel.textContent = 'ZONE/0' + (COLORWAY_ORDER.indexOf(prefs.colorway) + 1);
    for (const refs of rowRefs) {
      if (refs.row) renderRow(refs);
      if (refs.switchButton) refs.switchButton.setAttribute('aria-checked', String(prefs.dots));
    }
    const bar = panel.querySelector('.zone-bar');
    if (bar) bar.lastChild.textContent = sheetId();
  }

  /* ----------------------------------------------------------- atmosphere */

  let atmosphere = null;

  function buildAtmosphere() {
    atmosphere = el('div', 'zone-atmosphere');
    atmosphere.setAttribute('aria-hidden', 'true');
    atmosphere.appendChild(el('div', 'zone-cast'));
    atmosphere.appendChild(el('div', 'zone-halftone'));
    const tail = el('div', 'zone-halftone-tail zone-lens');
    const hot = el('div', 'zone-halftone-hot zone-lens');
    atmosphere.append(tail, hot);
    for (const corner of ['tl', 'tr', 'bl', 'br']) {
      atmosphere.appendChild(el('span', 'zone-tick zone-tick-' + corner));
    }
    (document.body || document.documentElement).appendChild(atmosphere);

    /* intro: the brackets fade in once per load */
    if (effectiveMotion() === 'full') {
      atmosphere.setAttribute('data-zone-intro', 'yes');
      window.setTimeout(() => atmosphere.removeAttribute('data-zone-intro'), 1500);
    }

    trackContentTop();
    trackPointer();
  }

  /* The top brackets hang under the app's titlebar: measured from the chat
     view when it exists, else from the window edge. Re-measured on resize. */
  function trackContentTop() {
    const root = document.documentElement;
    let frame = 0;
    const apply = () => {
      frame = 0;
      const view = document.querySelector('[data-testid="chat-view"]');
      const top = view ? Math.max(0, Math.round(view.getBoundingClientRect().top)) : 0;
      root.style.setProperty('--zone-content-top', top + 'px');
    };
    const queue = () => { if (!frame) frame = window.requestAnimationFrame(apply); };
    window.addEventListener('resize', queue);
    window.setInterval(queue, 2000);
    window.setTimeout(apply, 300);
    window.setTimeout(apply, 1500);
  }

  /* Pointer lens: two followers per frame — the head eases fast, the tail
     slow, so movement drags a short comet. The lens lights the sheet above
     the composer only: past the chat input's top edge it fades out where it
     stands. Motion off parks it off-panel. */
  function trackPointer() {
    if (!atmosphere) return;
    let frame = 0;
    let targetX = 0; let targetY = 0;
    let leadX = 0; let leadY = 0;
    let tailX = 0; let tailY = 0;
    let active = false;

    const composerTop = () => {
      const input = document.querySelector('[data-testid="chat-input"]');
      return input ? input.getBoundingClientRect().top : window.innerHeight;
    };

    const tick = () => {
      frame = 0;
      leadX += (targetX - leadX) * 0.3;
      leadY += (targetY - leadY) * 0.3;
      tailX += (targetX - tailX) * 0.05;
      tailY += (targetY - tailY) * 0.05;
      const rect = atmosphere.getBoundingClientRect();
      const style = atmosphere.style;
      style.setProperty('--zone-pointer-x', Math.round(leadX - rect.left) + 'px');
      style.setProperty('--zone-pointer-y', Math.round(leadY - rect.top) + 'px');
      style.setProperty('--zone-tail-x', Math.round(tailX - rect.left) + 'px');
      style.setProperty('--zone-tail-y', Math.round(tailY - rect.top) + 'px');
      if (Math.abs(targetX - leadX) > 0.4 || Math.abs(targetY - leadY) > 0.4
        || Math.abs(targetX - tailX) > 0.4 || Math.abs(targetY - tailY) > 0.4) {
        frame = window.requestAnimationFrame(tick);
      }
    };

    window.addEventListener('pointermove', (event) => {
      if (effectiveMotion() === 'off' || !prefs.dots) return;
      const inside = event.clientY < composerTop() - 8 && event.clientY > 0;
      if (!inside) {
        if (active) {
          active = false;
          atmosphere.setAttribute('data-zone-lens', 'off');
        }
        return;
      }
      targetX = event.clientX;
      targetY = event.clientY;
      if (!active) {
        active = true;
        leadX = targetX; leadY = targetY;
        tailX = targetX; tailY = targetY;
        atmosphere.removeAttribute('data-zone-lens');
      }
      if (!frame) frame = window.requestAnimationFrame(tick);
    }, { passive: true });

    const parkLens = () => {
      if (effectiveMotion() === 'off' || !prefs.dots) {
        atmosphere.setAttribute('data-zone-lens', 'off');
      }
    };
    parkLens();
    subscribe(parkLens);
  }

  /* ---------------------------------------------------------------- probe */

  /** Opt-in DOM probe. Enable with localStorage['zcode-zone-skin:probe']='1'
   *  and restart; the payload lands under 'zcode-zone-skin:diag' and reads
   *  directly in devtools. Answers in one shot: is the boot alive, which
   *  theme classes are on <html>, does the token layer resolve, where is the
   *  composer, is the atmosphere mounted. Off unless enabled; it writes only
   *  that one key and never mutates the document. */
  function probeOnce() {
    let enabled = false;
    try { enabled = window.localStorage.getItem(PROBE_FLAG) === '1'; } catch { /* off */ }
    if (!enabled) return;
    window.setTimeout(() => {
      const read = (element, name) => {
        try { return getComputedStyle(element).getPropertyValue(name).trim(); } catch { return null; }
      };
      const rectOf = (element) => {
        if (!element) return null;
        const box = element.getBoundingClientRect();
        return [Math.round(box.left), Math.round(box.top), Math.round(box.width), Math.round(box.height)];
      };
      const payload = {
        when: new Date().toISOString(),
        rev: REV,
        boot: 'zone-boot.js',
        htmlClass: document.documentElement.className,
        attrs: {
          skin: document.documentElement.getAttribute('data-zone-skin'),
          colorway: document.documentElement.getAttribute('data-zone-colorway'),
          canvas: document.documentElement.getAttribute('data-zone-canvas'),
          motion: document.documentElement.getAttribute('data-zone-motion'),
          dots: document.documentElement.getAttribute('data-zone-dots'),
        },
        brandOnHtml: read(document.documentElement, '--zone-brand'),
        cardOnHtml: read(document.documentElement, '--color-card'),
        brandOnBody: read(document.body, '--zone-brand'),
        prefs,
        atmosphere: rectOf(document.querySelector('.zone-atmosphere')),
        console: rectOf(document.querySelector('.zone-console')),
        chatInput: rectOf(document.querySelector('[data-testid="chat-input"]')),
        chatView: rectOf(document.querySelector('[data-testid="chat-view"]')),
        contentTop: read(document.documentElement, '--zone-content-top'),
        userPlate: (() => {
          const plate = document.querySelector('[data-v4-user-input-collapsible-content]');
          if (!plate) return null;
          const style = getComputedStyle(plate);
          return { background: style.backgroundColor, color: style.color };
        })(),
        viewport: [window.innerWidth, window.innerHeight],
        title: document.title,
      };
      try { window.localStorage.setItem(PROBE_KEY, JSON.stringify(payload)); } catch { /* full */ }
    }, 2500);
  }

  /* ----------------------------------------------------------------- boot */

  const start = () => {
    applyRoot();
    buildAtmosphere();
    buildConsole();
    renderConsole();
    probeOnce();

    /* the title can settle after boot; keep the device bar's sheet id honest */
    window.setInterval(() => { if (panel && !panel.hidden) renderConsole(); }, 4000);

    window.ZONE_SKIN = {
      rev: REV,
      getPrefs: () => ({ ...prefs }),
      update,
      subscribe,
      colorways: COLORWAY_ORDER,
      canvases: CANVAS_ORDER,
      motions: MOTION_ORDER,
    };
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
})();
