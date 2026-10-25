/**
 * Read the payload written by the client's opt-in probe.
 *
 * The probe stores JSON under `dsh-zone-skin:diag`. Chromium keeps localStorage
 * in a LevelDB where the *key* is plain bytes but the *value* is UTF-16LE (with
 * a one-byte encoding prefix), so the two must be decoded separately: decoding a
 * whole file one way can never match both.
 *
 * The payload must begin immediately after the key. Scanning further would
 * happily return a *neighbouring* record's JSON — a wrong answer that looks
 * right, which is worse than no answer.
 *
 * Enable the probe first:
 *
 *     localStorage['dsh-zone-skin:probe'] = '1'   then reload the app
 *
 * Run with: npm run probe:read
 * Testing aid: DSH_LEVELDB_DIR=/path/to/leveldb npm run probe:read
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const KEY = 'dsh-zone-skin:diag';

/** Where each platform's Electron build keeps Local Storage. */
function leveldbDirs() {
  if (process.env.DSH_LEVELDB_DIR) return [process.env.DSH_LEVELDB_DIR];
  const home = os.homedir();
  const appData = process.env.APPDATA || path.join(home, 'AppData', 'Roaming');
  const roots = [
    path.join(appData, '@deepseek-ai', 'dsh-desktop'),
    path.join(home, '.config', '@deepseek-ai', 'dsh-desktop'),
    path.join(home, 'Library', 'Application Support', '@deepseek-ai', 'dsh-desktop'),
  ];
  return roots.map((root) => path.join(root, 'Local Storage', 'leveldb'));
}

/** Parse the first balanced JSON object that starts at the beginning of text. */
function braceJson(text) {
  const body = text.replace(/^[\u0000\s]+/, '');
  if (!body.startsWith('{')) return undefined;
  let depth = 0;
  for (let i = 0; i < body.length; i += 1) {
    const ch = body[i];
    if (ch === '{') depth += 1;
    else if (ch === '}') {
      depth -= 1;
      if (depth === 0) {
        try {
          return JSON.parse(body.slice(0, i + 1));
        } catch (error) {
          return undefined;
        }
      }
    }
  }
  return undefined;
}

/** A probe payload always carries `when`; anything else is a different record. */
function isProbePayload(value) {
  return !!value && typeof value === 'object' && typeof value.when === 'string';
}

/**
 * The value starts within a couple of bytes of the key (the encoding prefix is
 * one byte), so only those alignments are tried. Every candidate must parse as a
 * payload that begins exactly there.
 */
function decodeValueAt(buffer, offset) {
  for (let shift = 0; shift <= 11; shift += 1) {
    const slice = buffer.subarray(offset + shift, buffer.length);
    for (const encoding of ['utf16le', 'utf8', 'latin1']) {
      const parsed = braceJson(slice.toString(encoding, 0, 2_000_000));
      if (isProbePayload(parsed)) return parsed;
    }
  }
  return undefined;
}

/** Last parseable payload for KEY in one file; later writes win. */
function lastPayload(buffer) {
  let found;
  for (const needle of [Buffer.from(KEY, 'utf8'), Buffer.from(KEY, 'utf16le')]) {
    let at = buffer.indexOf(needle);
    while (at >= 0) {
      const parsed = decodeValueAt(buffer, at + needle.length);
      if (parsed) found = parsed;
      at = buffer.indexOf(needle, at + 1);
    }
  }
  return found;
}

const dir = leveldbDirs().find((candidate) => {
  try {
    return fs.statSync(candidate).isDirectory();
  } catch (error) {
    return false;
  }
});

if (!dir) {
  console.error('No DSH Local Storage directory found. Is the desktop app installed for this user?');
  process.exit(1);
}

let payload;
for (const name of fs.readdirSync(dir).filter((file) => /\.(log|ldb)$/.test(file))) {
  const raw = fs.readFileSync(path.join(dir, name));
  payload = lastPayload(raw) || payload;
}

if (!payload) {
  console.error(`No ${KEY} payload yet.`);
  console.error(`Enable the probe first: localStorage['${KEY.replace(':diag', ':probe')}'] = '1', then reload.`);
  process.exit(1);
}

console.log(JSON.stringify(payload, null, 2));

/* The two questions worth reading first:
 *   aliasOnBody  non-empty and equal to brandToken  -> the alias layer resolves
 *   aliasOnHtml  empty                              -> expected: tokens live on <body>
 * Then compare `selected[].bg` with the accent colour you intended. */
