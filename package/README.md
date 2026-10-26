# ZONE skin

Black-and-orange hardware styling for the DeepSeek Harness Web UI, built from a
desk-setup reference: graphite chassis, hot orange accents, cream keycap paper,
die-cut sticker graphics and warm LED glow.

## What it changes

- **Color** 鈥?the whole surface is recolored through the theme token layer: warm
  graphite `#2c2927` panels (cards `#373330`, raised layers `#423d3a`), cream
  `#f8f3e8` text, orange `#ff6f1a` brand, chunky 4鈥?2px radii, orange focus
  rings and a sticker-orange toast. The UI face is Bahnschrift, the label face
  is Cascadia Mono.
- **Menus and popovers** 鈥?the menu material layer (`--dsw-menu-surface-fill`,
  translucent white in the app's light theme) is bound to the raised surface, so
  the slash-command list, model picker and every other menu render dark.
- **Selected rows and small controls** 鈥?the active session row in the sidebar is
  a solid colorway plate with dark ink (its caption tokens are overridden so the
  timestamp stays readable), the composer's round add button
  (`--dsw-specific-selector`, near-white in the light theme) becomes a raised
  graphite chip, and the composer's primary action (send / stop) plus the
  Agent's *deep diving* indicator — including its shimmer sweep — take the
  colorway instead of the app's blue accent.
- **Cursor** 鈥?the pointer set is the skin's own: 24px SVG glyphs (graphite fill
  with a colorway outline, or a cream halo plus colorway core for line art)
  published as `--zone-cursor*`, so they follow the active colorway and both
  canvases. Covers the default arrow (tailless, sharp barbs), text I-beam, hand,
  forbidden, split resize and image zoom. `wait`/`progress` (CSS cursor images
  cannot animate), `help`, `crosshair`, `grabbing`, `move` and `nwse-resize` keep
  the system glyphs, and the Electron window chrome stays native.
- **Elevation casts a deep-orange shadow** 鈥?the accent is mixed 58% (night) or
  45% (day) toward black, then layered as a crisp contact edge, a soft falloff
  and a 1px tint ring. Menus, popovers, dialogs, toasts and the sticker card use
  it.
- **Two plates cast a flat orange glow** 鈥?the sent-message plate and the
  selected session row keep their own fill and only cast light outward (4px +
  9px on the plate, 2px + 5px on the row); there is no rim and no inset, so the
  block reads as lit from behind rather than raised. The composer card is
  backlit rather than lit: a neutral 1px white hairline plus a restrained bloom
  (3.5px core, 8px halo, 7px underglow).
- **Sent messages** 鈥?the user message plate *is* the colorway accent
  (`--dsw-specific-bubble` = the same fill a selected session row takes), so the
  sidebar and the conversation never show two different versions of one colour.
  Its ink is always white (`--zone-plate-ink`), matching the accent-filled rows and
  buttons in every colorway and canvas 鈥?a deliberate choice even where white sits
  below 3:1 (night orange 2.78:1, night hazard yellow 1.57:1). The plate's selection
  highlight is inverted (white plate, ink text) so it stays visible on the fill. The
  rule is scoped to chat-flow rows, which covers all three host plates that read
  that token (message, steering and
  question-reply bubbles) and leaves the tooltip alone.
- **No white patches** 鈥?components that fall back to near-white through local
  variables (`--card-fill`, `--changes-fill`, `--deliverable-fill`,
  `--plan-card-fill`) or the light `--dsw-alias-button-elevated-fill` are bound
  to the skin surfaces, so the canvas stays coherent even when the app's own
  theme is light.
- **The inverted label follows the canvas, not the app** - the host titles every
  plate it fills with `--dsw-alias-label-primary` (the wordmark's `HARNESS`
  badge, the sidebar build-version pill) and with
  `--dsw-alias-button-contrast-fill` (the attachment remove key) using
  `--dsw-alias-label-primary-inverted`, and that token is published from the
  app's own light/dark mode: `#ffffff` in the light theme, `#353638` in the dark
  one. A forced night canvas running over a light-mode app therefore inherited
  the white label on a cream plate - white on cream, 1.11:1, so the `HARNESS`
  badge read as a blank pill. The token layer now binds the pair to the chassis:
  `label-primary-inverted` takes the opposite canvas ink (`#171310` on night,
  `#f8f3e8` on day) and `button-contrast-fill` takes the label ink, so the plate
  reads like the app's own dark theme on either canvas.
- **Atmosphere** 鈥?a fixed layer adds a 7px halftone screen and four taped
  corner brackets; the corners fade in once on load. The two top brackets hang at
  the top of the chat scroller 鈥?under the title row and the tab strip 鈥?not on
  the panel's own edge, and that inset is measured at runtime, so the brackets
  follow the header instead of being cut by it. The sheet itself carries no
  colour wash, so the conversation panel stays the plain chassis colour. Along the
  sheet's left edge a 7.5px edge gradient (peak alpha 0.2) tinted cool black reads
  as a cold seam between the sidebar and the panel; it is clipped by the panel's
  rounded top-left corner, sits under the halftone and the corner brackets, and
  drops out when the sidebar collapses to its rail. The titlebar draws the same
  7.5px curve down onto the sheet's top edge; its left end crossfades over the sidebar
  band so the two edges never stack, and it stays when the rail is in. Set
  `--zone-cast-tint` to `var(--zone-brand)` for the colorway accent, `#fff` for a
  white edge, or `#000` for a neutral cast.
  Over the chat area a pointer lens lights the same grid with square dots in the
  colorway accent. The head (100px radius) is written straight from the pointer
  event and never lags the mouse; behind it a canvas repaints the same 4px squares
  on the same 7px grid from the pointer samples every frame, each cell taking the
  level of the freshest pass over it, so a sweep leaves a dotted wake instead of a
  second, larger circle easing along. The wake is the same size as the head — the
  same 100px radius and the same mask curve, dimming outward — and its peak is 9.5%
  against the head's 10%, so it always reads as the head's tail rather than a
  second light. A sample lives 1.1 s: up to then the cell dims continuously, and at
  that point it stops being painted at all, which is what makes the wake reach the
  sheet colour exactly — no alpha floor, and crossing the same cells again
  re-lights them rather than stacking into a bright patch. The head fades out over
  the composer card and device bar and when the pointer leaves the chat; the wake
  finishes its own fade. Motion `off` disables both.
- **Sidebar foot console** 鈥?a colorway dropdown (swatch + name) built on the
  app's own `Menu` primitive, so it shares the Agent menus' surface, item and
  keyboard behaviour, plus a canvas key; in the collapsed rail it becomes a
  single cycling chip.
- **New-session key** 鈥?the sidebar's *new session* button is the only
  new-conversation control the app has, and it ships as a neutral grey. Hover,
  keyboard focus or press turns it into the colorway plate: accent fill, white
  label, the selected row's bloom, with the shortcut hint dimmed to 72% white. The
  same rule covers the collapsed-rail copy, which is the same element.
- **Device bar** under the composer 鈥?pulsing LED, hazard-tape rule, the active
  colorway number and the current sheet id.
- **Sticker mark** in the blank-session hero 鈥?a die-cut sticker drawn as SVG
  (graphite plate, colorway border, cream Z, three LED segments).
- **Settings row** — *Settings → General → ZONE skin*: canvas, colorway, motion,
  halftone toggle, and a cream sticker specimen.
- **Completion chime** — when a session's task finishes (its agent leaves the
  running state), the plugin plays the embedded task-complete chime. The sound is a
  58 KB MP3 base64-encoded inside `client.js` (the bundle route serves only the
  `./client` export, so a binary sibling asset could not travel with the
  package). Detection rides the forwarded `api-session/status` projection:
  `ctx.remote.$on('api-session/status')` reports `(sessionId, running)` on every
  agent status flip, and `api-session/added` summaries mark subagent children
  (`origin: "subagent"` / `parentSessionId`), so one-shot subagents finishing
  inside a parent task stay silent — only sessions the sidebar lists chime, and
  only when the browser saw them start running. The settings row adds a switch,
  three volume steps and a test button; the test button sounds the chime even
  while the preference itself is off.

## Canvases and colorways

| Canvas | Surface | Text |
| --- | --- | --- |
| Blacksite (night) | graphite `#2c2927`, cards `#373330` | cream `#f8f3e8` |
| Cream (day) | keycap cream `#e8e1d1`, cards `#f5efe4` | ink `#171310` |

| Colorway | Night accent | Day accent |
| --- | --- | --- |
| Zone orange | `#ff6f1a` | `#e2560d` |
| Ember | `#ff4632` | `#c62c1b` |
| Hazard | `#ffc61a` | `#a8770a` |
| Cobalt | `#4d94ff` | `#1f5fd6` |

The chassis never changes between colorways 鈥?only the accent, exactly like a
hardware colorway. `Canvas` is *Follow app*, *Cream* or *Blacksite*; forcing one
canvas maps both light and dark entries so the app's own preference cannot
split the skin.

Preferences live in `localStorage` under `dsh-zone-skin:prefs`. Motion follows
the system `prefers-reduced-motion` setting regardless of the plugin value.

## Chinese font (prerequisite — read this before installing)

The stylesheet names **`Noto Sans Mono CJK SC`** for Chinese. The font is *not*
bundled: the two weights are 31.8 MB of OTF, which is more than the rest of the
package by two orders of magnitude, so it is installed once per machine instead.

```powershell
# from the repo, before or after wiring the profile — one time per machine
powershell -ExecutionPolicy Bypass -File font-lab\install-fonts.ps1
```

The script copies the two weights into `%LOCALAPPDATA%\Microsoft\Windows\Fonts` and
registers them under `HKCU` — no administrator, no installer. Manual alternative:
double-click the two `.otf` files in `font-lab/fonts/`.

- **Restart the app afterwards** — the renderer enumerates system fonts only at
  startup, so the first run after installing still paints the fallback.
- Without the font the chain goes straight to `Microsoft YaHei` (a tightened Maple
  build was tried and removed on request). The UI still works, but Chinese comes out
  wider and no longer matches the specimen sheets.
- The font is SIL OFL 1.1; redistributing the `.otf` files requires keeping its
  licence alongside them.

## Bundle layout

| File | Purpose |
| --- | --- |
| `cordis.patch.yml` | inserts the `zone-skin` row with default config |
| `index.js` | Host half — no host work to do |
| `client.js` | Client half: token layer, stylesheet, five slot registrations |
| `locale/{en,zh}.json` | Plugin Manager title and description |
| `icon.svg` | Original artwork for the plugin row |
| `NOTES.md` | Debugging field notes 鈥?read this before chasing a colour that "does not apply" |

Config accepted by the row (all optional): `colorway` (`zone`, `ember`,
`hazard`, `cobalt`), `canvas` (`auto`, `day`, `night`), `motion` (`full`,
`quiet`, `off`), `dots` (boolean), `chime` (boolean, default true),
`chimeVolume` (`low`, `mid`, `high`). `chime`/`chimeVolume` also live in the
`dsh-zone-skin:prefs` localStorage record the settings row writes.

## Slots used

All are additive seats, so nothing shipped is replaced:

- `shell.overlay` 鈫?`zone.atmosphere`
- `sidebar.footer.action` 鈫?`zone.console`
- `conversation.hero.brand.mark` 鈫?`zone.mark`
- `conversation.composer.dock` 鈫?`zone.bar`
- `settings.general.item` 鈫?`zone.skin`

## Checks

```sh
npm run check
```

`tests/token-contrast.mjs` loads the Client module with a stub module table and
asserts that every colorway/canvas pair produces a complete token layer of
`{ light, dark }` strings, that shadows are valid CSS, and that the text pairs
the tokens control keep their contrast floors (body 7:1, secondary 4.5:1,
badges 3:1).

`tests/css-coverage.mjs` asserts that every component class the Client renders is
styled by the stylesheet and that its braces balance.

`tests/chime-behavior.mjs` drives the forwarded `api-session/*` events against a
stub ctx/Audio: a delegation child finishing inside a parent task stays silent, a
top-level completion chimes exactly once, an idle flip the browser never saw start
stays silent, and the settings row renders the switch, three volume steps and the
test button.

## When a style "does not apply"

Read [NOTES.md](NOTES.md) before guessing. The short version:

- The harness publishes its `--dsw-*` tokens on `<body>`, so this skin's alias
  block must be declared on `html[data-zone-skin] body`. Declared on `<html>`,
  each alias computes to the guaranteed-invalid value (empty string) and every
  rule reading it is silently dropped 鈥?the stylesheet layer dies while the token
  layer keeps working.
- An override carrying `!important` and an invalid value removes the owner's
  styling rather than replacing it, which is why a row can end up with no
  background at all.
- For anything selector-related, enable the opt-in probe
  (`localStorage['dsh-zone-skin:probe'] = '1'`, reload, then
  `npm run probe:read`) and read the real class strings, resolved aliases and
  computed colours instead of inferring them from build hashes.
## Moving to another machine

`npm pack` writes a tarball containing the source, the tests and both docs — **not**
the Chinese font. Two things travel separately:

1. **the font** — run `font-lab/install-fonts.ps1` on the target machine (or
   double-click the `.otf` files in `font-lab/fonts/`), see *Chinese font* above;
2. **the tarball** — unpack it, point a DSH profile at it (`link:` for live editing,
   `file:*.tgz` for a frozen snapshot), run `pnpm install` in the profile, then
   **restart the desktop app** — a page refresh does not reload client plugins.

[AGENTS.md](AGENTS.md) → *Packaging and moving to another machine* has the exact
commands.

