import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const publicDir = path.join(root, 'public');
const html = await fs.readFile(path.join(publicDir, 'index.html'), 'utf8');
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
assert.equal(new Set(ids).size, ids.length, 'Duplicate section IDs');
const references = [...html.matchAll(/\b(?:src|href|poster|data-src)="([^"]*)"/g)].map(m => m[1]);
for (const match of html.matchAll(/\bsrcset="([^"]+)"/g)) {
  references.push(...match[1].split(',').map(v => v.trim().split(/\s+/)[0]));
}
for (const reference of new Set(references)) {
  if (!reference || /^(?:https?:|mailto:|tel:|data:)/.test(reference)) continue;
  if (reference.startsWith('#')) {
    assert(ids.includes(reference.slice(1)), `Missing anchor: ${reference}`);
    continue;
  }
  assert(!reference.startsWith('/'), `Root URL breaks project hosting: ${reference}`);
  const local = path.resolve(publicDir, decodeURIComponent(reference.split(/[?#]/)[0]));
  assert(local.startsWith(publicDir + path.sep), `Escaping public folder: ${reference}`);
  assert((await fs.stat(local)).isFile(), `Missing file: ${reference}`);
}
assert(!html.includes('portrait-editor'), 'Static hosting must not expose a server-only portrait editor');
const projects = [...html.matchAll(/<article\b[^>]*id="([^"]+)"/g)].map(m => m[1]);
const catalog = JSON.parse(await fs.readFile(path.join(root, 'content.json'), 'utf8'));
assert.deepEqual(projects, catalog.map(p => p.id), 'Project order differs from catalogue');
assert.equal((html.match(/<video\b[^>]*data-src=/g) || []).length, catalog.filter(p => p.video).length);
assert.equal((html.match(/class="render-link"/g) || []).length, catalog.flatMap(p => p.images).length);
assert.equal((html.match(/class="drawing-sheet"/g) || []).length, catalog.flatMap(p => p.drawings).length);
console.log(`Validated ${projects.length} projects, ${catalog.filter(p => p.video).length} films, ${catalog.flatMap(p => p.images).length} renders, ${catalog.flatMap(p => p.drawings).length} drawing sheets and all local URLs.`);
