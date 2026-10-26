# Field notes: debugging this skin

Written after a session where the selected session row showed no accent colour
and several rounds were spent guessing at selectors. Everything below is what
would have short-circuited that. Read this before touching colours that "do not
apply".

## The one rule that explains most silent failures

**The harness publishes its `--dsw-*` tokens on `<body>`. Every alias of this
skin therefore has to be declared on `<body>` too.**

```css
/* correct */
html[data-zone-skin] body { --zone-brand: var(--dsw-alias-brand-primary); }

/* silently broken */
html[data-zone-skin]      { --zone-brand: var(--dsw-alias-brand-primary); }
```

Why it fails silently: a custom property whose `var()` cannot resolve at its own
element computes to the *guaranteed-invalid* value, which serialises as the empty
string. Nothing warns. Then every declaration that reads it — `background:
var(--zone-brand)` — becomes invalid at computed-value time and is **dropped**,
so the property falls back to its initial value. For `background` that is
`transparent`, which reads as "this element has no styling at all".

Symptom shape: the token layer (colours, radii, fonts) works, because that runs
through `ctx.theme.overrideTokens()` in JS, while the stylesheet layer appears
dead — glow, brackets, console, bubbles, selected rows, all inert.

Diagnostic: read `--zone-brand` from both elements. On `<body>` it must be
non-empty; on `<html>` it is expected to be empty. See the probe below.

## The `!important` trap

Overriding an owner rule with an invalid value is worse than not overriding it.
The harness paints the selected session row with
`var(--dsw-alias-interactive-bg-hover)`; a skin rule carrying
`background: var(--zone-brand) !important` wins the cascade and then throws the
declaration away, so the row loses even the owner's subtle tint and ends up with
no background whatsoever. When an override "does nothing", check that the value
it supplies actually resolves first.

## Probe first, guess never

Class hashes in the harness bundle (`wnFoaW_sessionRow`) are stable per build but
meaningless to read; guessing which component paints a row wastes rounds. The
client carries an opt-in probe that dumps the real DOM state instead.

Enable it once, in the app's devtools console:

```js
localStorage['dsh-zone-skin:probe'] = '1';
```

Reload the app, wait ~3 seconds, then read the payload from disk:

```sh
npm run probe:read
```

What it answers, in one shot:

| Field | Reading |
| --- | --- |
| `attrs` | is `data-zone-skin` actually on `<html>` |
| `aliasOnHtml` / `aliasOnBody` | the trap above, in two strings |
| `brandToken` / `hoverToken` | which `--dsw-*` tokens the harness publishes on `<body>` |
| `stylesheets` | whether the `<style data-plugin>` node is mounted, and its size |
| `slots` | the real `data-slot` names — the stable selector hooks |
| `selected[]` / `sessionRows[]` | real class strings, computed `bg` and `color`, `aria-selected` |

The reader only accepts a payload that begins immediately after the key and
carries a `when` field. That restriction is deliberate: a looser scan happily
returns a *neighbouring* localStorage record (a draft, a preference) and looks
perfectly valid, which is a worse failure than finding nothing. To test the
reader itself, point it at a copied leveldb directory:
`DSH_LEVELDB_DIR=... npm run probe:read`.

The probe is off unless the flag is set, writes only that one key, and never
mutates the document. Turn it off with
`localStorage.removeItem('dsh-zone-skin:probe')`.

## Sidebar session rows

The harness paints hover and selection through the **same** token:

```css
.projectRow:hover, .sessionRow:hover, .sessionRow.selected {
  background: var(--dsw-alias-interactive-bg-hover);
}
```

So a token override alone can never separate them — the difference is only
visible through the state class. Observed on the real element:

```
class = "wnFoaW_sessionRow wnFoaW_selected"   aria-selected = "true"
```

Both hooks work, and the rule in `client.js` matches both on purpose. The prefix
before the first `_` is the build hash: never select on it. Match the suffix with
`[class*="_sessionRow"]`, and prefer `aria-selected` where the component exposes
it.

## Ink on the accent

Everything that sits on the colorway accent uses **white** ink, on purpose: the
selected session row, the sent-message plate, the text selection, and the active
workspace row. A dark ink was tried on the selection and rejected — on a lit plate
it reads as a separate element and breaks the family resemblance with the other
three surfaces.

Because the host's own surfaces (PDF text layer, code editors, document view) ship
their own selection colours, `::selection` is pinned with `!important` and a
literal ink. A derived value loses that fight **silently**, which is exactly how
the selection ended up light-on-orange with no obvious cause. The inverted rule for
orange user bubbles also carries `!important` — it has to outrank the global pin,
or the selection becomes orange-on-orange and disappears.

Two things worth remembering from the debugging session:

- `--dsw-alias-label-primary-foreground` is the ink for *filled plates* (primary
  buttons, toasts) and looks like the right family here, but it is a **cream** and
  the host overrides it on `<body>`. Chaining to it left the selected row visibly
  warmer than the pinned text selection. `--zone-brand-on` is therefore a literal
  `#ffffff`, and a computed read — never the palette arithmetic — is what settles
  which value actually wins.
- White on `#ff6f1a` is roughly 2.4:1. When legibility matters more than the
  lit-plate look on a given surface, deepen the plate with the existing `BUBBLE`
  orange (`#d2450f`) — that constant exists precisely for white ink.

## The inverted label belongs to the app, not to the canvas

`--dsw-alias-label-primary-inverted` is not a free colour: the host titles every
plate it fills with `--dsw-alias-label-primary` (the wordmark's `HARNESS` badge,
the sidebar build-version pill) and with `--dsw-alias-button-contrast-fill` (the
attachment remove key) using it. The host defines it per *its own* theme:
`#ffffff` in the light theme, `#353638` in the dark one.

The skin overrode the plate and left the ink alone. On a machine where the skin
forces the **night** canvas while Windows — and so the app's `ui-theme` preference
`system` — runs in **light** mode, the plate became the cream ink while the
letters stayed `#ffffff`: 1.11:1, so the badge read as a blank cream pill. A
machine whose app is genuinely dark got `#353638` letters and looked correct,
which is why it failed on one box only.

Measured, not guessed: sample the badge in a screenshot. Plate `#f8f3e8` (the
skin's night ink) plus letters `#ffffff` (the app's light-theme inverted label)
proves the two modes disagree on the same element.

The fix binds both tokens of the pair to the chassis (`invertInk` in `schemeFor`):
`label-primary-inverted` becomes the opposite canvas ink, `button-contrast-fill`
becomes the label ink. Rebinding the ink alone would have regressed the
attachment's remove key, whose fill still came from the app's light theme
(`#61666b`) — pair them exactly as the host's own dark theme does.

## Two facts that cost the most time

Both were measured, not reasoned about, and both would have saved a long detour:

- **A page refresh does not reload client plugins in this build.** Editing
  `client.js` and pressing Ctrl+R keeps serving the previous module; a full restart
  of the desktop app is what applies a change. Every "the fix did nothing" moment in
  that session was this.
- **`data-slot` elements are zero-size mount wrappers.** Measured across the whole
  shell — `root`, `sidebar`, `main.conversation`, `conversation.composer.bar`,
  `conversation.chat.flow` — every one reports a `0x0` rect. They are anchors for
  `register()`, not layout boxes. Never measure a slot to place something: seed from
  a painted child (the composer card) and bound any ancestor walk with a real
  landmark such as the sidebar's right edge, or the walk climbs to the window.

## The atmosphere layer

`shell.overlay` is the only free seat for a frame-wide layer, so the halftone and the
corner brackets are rendered there and then **anchored to the conversation panel** at
runtime: the panel rect is measured and published as `--zone-panel-*`, and the layer
positions itself from those instead of from the window. The panel is found by slot
(`main.conversation`, then `conversation.view`, then `main`); the probe reports which
one matched under `panel`, so a wrong guess is one read away from being corrected.
Re-measurement runs on window resize, on the panel's own resize, and on a 1 s poll,
because collapsing the sidebar moves the panel without resizing it.

The layer used to carry a warm radial wash as well. It was removed after review: the
panel keeps the chassis colour exactly, and only the halftone screen and the four
taped corners remain as atmosphere.

## Checklist before concluding "the skin is broken"

1. Is the root attribute on `<html>`? (`attrs` in the probe)
2. Is the `<style data-plugin>` node mounted? (`stylesheets`)
3. Does the alias resolve **on `<body>`**? (`aliasOnBody` non-empty)
4. Does the affected element actually carry the class you select on? (`selected[]`)
5. Is the value you supply valid CSS after every `var()` resolved? An invalid
   value with `!important` removes the owner's styling instead of replacing it.
6. Did the app reload? A page refresh picks up `client.js`, but a change made
   while the app was already running is not guaranteed to be live — when in
   doubt, restart the desktop app.

## Testing

```sh
npm run check          # syntax + token layer + CSS coverage
npm run probe:read     # read the probe payload (after enabling it)
```
