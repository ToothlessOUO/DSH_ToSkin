# AGENTS.md — working on the ZONE skin

Instructions for an agent (or a human) picking this package up cold, possibly on a
different machine. Read this first; it is the compressed result of a long debugging
session.

## What this package is

A local client plugin (`@local/dsh-zone-skin`) for the **DeepSeek Harness** desktop
app. It recolours the Web UI through two layers:

1. **Token layer (JS)** — `ctx.theme.overrideTokens(ID, tokensFor(prefs))` publishes
   `--dsw-*` design tokens. This runs on the host's theme pipeline and reaches
   `<body>`.
2. **Stylesheet layer (CSS)** — a `<style data-plugin>` element built from the `CSS`
   template in `client.js`, addressing host components by stable-ish selectors.

Everything visual is one of those two. When a colour "does not apply", decide which
layer owns it before editing anything.

## Environment facts (verified on Windows, current DSH desktop build)

| Fact | Value |
| --- | --- |
| Harness app (Windows) | `%LOCALAPPDATA%\Programs\DeepSeek Harness` |
| Host code (packed) | `resources\app.asar` — CSS/JS readable by scanning the archive |
| Profile that loads this plugin | `%USERPROFILE%\.dsh\profiles\desktop` |
| Wiring | profile `package.json` → `"@local/dsh-zone-skin": "link:<abs path to this dir>"` |
| Browser storage (for the probe) | `%APPDATA%\@deepseek-ai\dsh-desktop\Local Storage\leveldb` |
| Client entry | `client.js` (plain ESM, no build step) |

**Apply a change by restarting the desktop app.** A page refresh (Ctrl+R) keeps
serving the previous client module in this build — measured, not assumed. Nearly
every "the fix did nothing" moment traces back to this.

## Verify loop

```sh
npm run check          # syntax + token layer + CSS coverage   (must stay green)
npm run probe:read     # read the DOM probe payload from leveldb
```

There is no build step and no dev server: edit `client.js`, run `npm run check`,
restart the app.

## The probe (use this before guessing)

`probeOnce()` in `client.js` dumps real DOM state to `localStorage`. It is **on
only when enabled**:

```js
localStorage['dsh-zone-skin:probe'] = '1';   // then restart
```

Keys it writes:

| Key | Contents |
| --- | --- |
| `dsh-zone-skin:diag` | full payload: attrs, token values, stylesheets, slots, selected rows, slot boxes |
| `dsh-zone-skin:geom` | small ASCII-only geometry snapshot: viewport, layer, vars, panel, body |
| `dsh-zone-skin:boot` | **temporary** load marker (timestamp + `layer`/`nolayer`) |
| `dsh-zone-skin:prefs` | the user's preferences (written by normal use) |

`npm run probe:read` decodes `diag`. It requires the payload to start immediately
after its key and to carry `when`; a looser scan returns a *neighbouring*
localStorage record and looks valid, which is worse than failing.

Reading leveldb from outside the browser has three traps, all hit in practice:

- The `.log` file is held by Chromium: open it with a shared handle
  (`.NET FileShare::ReadWrite`, or copy first) or the read fails with
  `PermissionError`/`EPERM`.
- Large values are **split at block boundaries** with trailer bytes inserted mid
  value. That is why `geom` exists: it is small enough to survive in one fragment.
- Values containing non-ASCII are stored **UTF-16LE**; ASCII-only values are not.
  Decode the value separately from the key (the key is plain bytes).

If `probe:read` says "no payload", check `dsh-zone-skin:boot` first: no marker means
the app never loaded this build (see the restart note above).

## Invariants — break these and the skin silently dies

1. **Alias block lives on `html[data-zone-skin] body`.** The host publishes `--dsw-*`
   on `<body>`; an alias declared on `<html>` cannot resolve, computes to the
   guaranteed-invalid value (empty string), and *every* rule reading it is dropped.
2. **`data-slot` elements are zero-size mount wrappers.** Measured `0x0` for `root`,
   `sidebar`, `main.conversation`, `conversation.composer.bar`,
   `conversation.chat.flow`. Never measure a slot for geometry. Seed from a painted
   child (the composer card) and bound ancestor walks with the sidebar's right edge.
3. **Ink on the accent is white.** `--zone-brand-on: #ffffff` is a literal, not a
   chain to `--dsw-alias-label-primary-foreground` (a cream that the host overrides
   on `<body>`). Selection, selected session row, pressed chips, sticker, tape and
   the sidebar's new-session key (hover / focus / press) all read it. The chat plate
   reads `--zone-plate-ink`, which is the same white (next invariant).
4. **The chat plate *is* the colorway accent, and its ink is always white.**
   `schemeFor` sets `bubble = brand` — no second table of hand-picked plate
   colours — so the sent-message fill and a selected session row are the same
   colour in all four colorways and both canvases and cannot drift apart. The plate
   ink is the same literal white as `--zone-brand-on`, in every colorway and canvas;
   the owner chose one white voice over the extra contrast the chassis ink would add
   on the two brightest accents (night zone orange 2.78:1, night hazard yellow
   1.57:1). The contrast test pins plate == accent and ink == `#ffffff`. Do not
   reintroduce a dark fallback without asking.
   Do not "fix" a plate back to a deepened tone (cobalt's old `#1f5fd6`/`#1a52b8`,
   the warm plates' `#d2450f`-style tones) without asking either: a deep plate read
   as a second, heavier colour next to the sidebar.
5. **Hover and selection of a session row share one token**
   (`--dsw-alias-interactive-bg-hover`). Only the state class separates them:
   `[class*="_sessionRow"][class*="_selected"]` / `[aria-selected="true"]`.
   The hash prefix before `_` is per-build — never select on it.
6. **`::selection` is pinned with `!important`.** Host surfaces (PDF text layer, code
   editors) ship their own selection colours; a derived value loses that fight
   silently. The inverted rule for accent user plates also carries `!important`, or
   accent-on-accent makes the selection vanish.
7. **Only `shell.overlay` is a free seat** for a frame-wide layer; `main.conversation`
   and friends are occupied by host packages.

## File map

| File | Role |
| --- | --- |
| `client.js` | the whole plugin: palettes, token layer, CSS template, probe, components |
| `cordis.patch.yml` | inserts the plugin row with default config |
| `index.js` | host half — empty; the font install is a prerequisite, not host work |
| `locale/{en,zh}.json` | plugin-row title/description |
| `icon.svg` | plugin-row artwork |
| `tests/token-contrast.mjs` | token layer completeness + contrast floors |
| `tests/css-coverage.mjs` | every rendered class is styled, braces balanced |
| `tests/chime-behavior.mjs` | chime heard/silenced cases + settings row render |
| `tests/probe-read.mjs` | leveldb → probe payload reader |
| `NOTES.md` | the narrative version of the debugging session |
| `AGENTS.md` | this file |

## Fonts

The stylesheet names `Noto Sans Mono CJK SC` for Chinese (`FONT_SANS`, `FONT_MONO` in
`client.js`). The face is a **prerequisite of the machine, not part of this bundle** —
31.8 MB of OTF is too much to ship with a skin, and the plugin cannot hand a font file
to the renderer anyway (the CSS only names a family).

- Install it with `font-lab/install-fonts.ps1` (copies the two weights into
  `%LOCALAPPDATA%\Microsoft\Windows\Fonts` and registers them under HKCU — no admin),
  or by double-clicking the `.otf` files in `font-lab/fonts/`.
- The renderer enumerates fonts when it starts: **restart once** after installing.
- Without it the chain goes straight to `Microsoft YaHei` — the tightened Maple build
  was removed from both stacks on request; do not add it back. The skin still works,
  but Chinese is wider and off-specimen.
- `index.js` is an empty shell again. Do not put the font install back in it unless
  the owner asks — it was tried and rejected for package size.

## Current state (carry this forward)

- **The sidebar cast shadow lives inside the atmosphere.** `.zone-cast` is the first
  child of `.zone-atmosphere`: a 30px `to right` gradient (peak alpha 0.1) clipped by
  the panel's top-left corner and painted before the halftone and the corner
  brackets, so the dots and marks stay lit on the shadow. It drops out through
  `html[data-zone-skin] [data-sidebar-collapsed] .zone-cast` (the frame attribute the
  layout publishes while the rail is in) and fades for .22s. The only colour knob is
  `--zone-cast-ink` from the alias block: neutral black on the graphite chassis, warm
  brown on the cream one, same strength on both. It is CSS-only — not in `tokensFor`,
  so the token test does not see it. The atmosphere's `border-radius` is **top-left
  only** on purpose: the host panel has one rounded corner, and an all-corner radius
  cut a 16px notch out of the cast shadow at the window's bottom-left.
- **Atmosphere anchoring is implemented but unverified on the author's machine.** The
  layer is a `shell.overlay` div positioned from `--zone-panel-*`, measured at runtime
  by `ZoneAtmosphere`. Expected after a restart with a 1280×822 viewport:
  `vars ≈ ["280px","40px","1000px","782px", ...]` plus `--zone-panel-content-top`
  (the chat scroller's offset inside the panel) and `layer` matching the rect, i.e.
  the halftone and the four corner brackets confined to the conversation panel. The
  warm radial wash was removed, so the panel stays the plain chassis colour. If `vars`
  still reads `0/0/1280/822`, the panel finder walked too far — inspect `geom.panel`
  and `diag.sidebar`. The two **top** brackets hang from
  `--zone-panel-content-top`, i.e. under the title row and the tab strip, so they are
  never cut by the header; if that variable reads `0px`, `[class*="_scrollBody"]` was
  not found and the brackets fall back to the panel edge. The bottom pair stays on
  the panel edge on purpose.
- **Temporary diagnostics still present in `client.js`** and must be removed once the
  above is confirmed: the forced `enabled = true` in `probeOnce()` and the
  `dsh-zone-skin:boot` marker block. Both are marked `TEMPORARY` in the source.
- **Completion chime (R8) rides the forwarded api-session projection — do not
  "fix" it onto `session/event`.** The host's `session/event` feed is NOT in
  `API_REMOTE_FORWARDED_EVENTS` (api-remotes), so `ctx.on('session/event')` in a
  browser plugin never fires. The browser half of `dsh-client-store` consumes
  `ctx.remote.$on('api-session/status', (sessionId, running))` — emitted from
  the host's `agent/status` (`'idle' | 'running'`, collapsed to a boolean) — and
  `ctx.remote.$on('api-session/added', summary)`, whose summary carries
  `parentSessionId` / `origin: 'subagent'` for delegation children. The chime
  fires on a seen running→idle flip of a non-child session only; the module now
  also injects `'remote'` (still guarded at runtime). The 58 KB MP3 is embedded
  as base64 in `client.js` (`CHIME_MP3_B64`) because `/plugins` serves only the
  `./client` export — never try to fetch a sibling binary asset.

## Packaging and moving to another machine

```sh
npm pack          # → local-dsh-zone-skin-1.0.0.tgz (source, tests and docs included)
```

Install into a fresh profile:

```sh
# 0. the Chinese face (NOT in the tarball — 31.8 MB, see Fonts)
powershell -ExecutionPolicy Bypass -File <repo>/font-lab/install-fonts.ps1
# 1. unpack anywhere permanent, e.g. ~/src/zone-skin
tar -xzf local-dsh-zone-skin-1.0.0.tgz
# 2. point the profile at it (edit %USERPROFILE%\.dsh\profiles\desktop\package.json)
#    "dependencies": { "@local/dsh-zone-skin": "link:<abs path>/package" }
# 3. install and restart the app
cd %USERPROFILE%\.dsh\profiles\desktop && pnpm install
```

`link:` keeps the live-editing loop (edits apply on restart). Use
`file:<path>.tgz` instead for a frozen snapshot. The plugin must also appear in the
profile's `dsh.profile.bundles` if it is meant to load unconditionally — a linked
dependency alone is enough only when its `cordis.patch.yml` row is already inserted.
