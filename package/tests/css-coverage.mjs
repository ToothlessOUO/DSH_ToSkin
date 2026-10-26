// Development check: every class the components render exists in the stylesheet.
import fs from 'node:fs';

const here = new URL('.', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const src = fs.readFileSync(here + '/../client.js', 'utf8');
const startMarker = 'const CSS = `';
const start = src.indexOf(startMarker) + startMarker.length;
// Close on the line that holds only the terminating backtick, so a renamed or
// re-spaced section comment below the stylesheet cannot break this check.
const rest = src.slice(start);
const closeAt = rest.search(/^`;[ \t]*$/m);
if (start < startMarker.length || closeAt < 0) throw new Error('stylesheet block not found');
const css = rest.slice(0, closeAt);

const names = new Set();
for (const match of src.matchAll(/className: '([^']+)'/g)) {
  for (const token of match[1].split(/\s+/)) if (token.startsWith('zone-')) names.add(token);
}
for (const match of src.matchAll(/className: (['"])(zone-[a-z-]+)/g)) names.add(match[2]);
names.add('zone-console');

const missing = [...names].filter((name) => !css.includes('.' + name));
const open = (css.match(/\{/g) ?? []).length;
const close = (css.match(/\}/g) ?? []).length;
console.log('component classes: ' + names.size);
console.log('missing in CSS: ' + (missing.length ? missing.join(', ') : 'none'));
console.log('stylesheet rules: ' + open + ' blocks, braces ' + (open === close ? 'balanced' : 'UNBALANCED'));
if (missing.length || open !== close) process.exitCode = 1;
