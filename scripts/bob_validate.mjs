#!/usr/bin/env node
// scripts/bob_validate.mjs — CANONICAL BOB anti-vibe gate (copy into each project).
// Run: node scripts/bob_validate.mjs [--strict] [project-root]
//
// Generic checks (project-agnostic):
//   1. constitution.md exists at root.
//   2. Every specs/**/*.spec.md has frontmatter (id,type,version,status,owner) and a
//      "## Verification" section naming a real file.
//   3. Governance: any constitution/spec containing "pending core ratification" => WARN
//      by default, ERROR under --strict (unratified deviation is drift until core ratifies it).
//
// CRLF-SAFE: all content is normalised \r\n -> \n before parsing. (Earlier versions
// failed on Windows checkouts — every Galaxy project needed a CRLF-fix commit. Fixed here
// once and for all.)
//
// PROJECT-SPECIFIC DRIFT CHECKS: add them in the marked section near the bottom
// (e.g. "schema spec column X must match code Y"). Keep the generic core unchanged.

import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join } from 'node:path';

const args = process.argv.slice(2);
const strict = args.includes('--strict');
const roots = args.filter((arg) => arg !== '--strict');
const ROOT = roots[0] ?? process.cwd();
const errors = [];
const warnings = [];
const read = (p) => readFileSync(p, 'utf8').replace(/\r\n/g, '\n');

// 1. constitution
if (!existsSync(join(ROOT, 'constitution.md'))) {
  errors.push('Missing constitution.md at project root.');
}

function walk(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
}

// 3 (scan): governance deviation marker across constitution + specs
for (const f of [join(ROOT, 'constitution.md'), ...walk(join(ROOT, 'specs'))].filter(existsSync)) {
  if (/pending core ratification/i.test(read(f))) {
    const msg = `${f.slice(ROOT.length + 1).replace(/\\/g, '/')}: contains an UNRATIFIED deviation (pending core ratification) — ratify in the core constitution + FLEET.md.`;
    (strict ? errors : warnings).push(msg);
  }
}

// 2. specs
const specs = walk(join(ROOT, 'specs')).filter((f) => f.endsWith('.spec.md'));
if (specs.length === 0) errors.push('No specs found under specs/**.');

const REQUIRED_KEYS = ['id', 'type', 'version', 'status', 'owner', 'depends_on', 'consumed_by'];
const ids = new Map();
const PATH_RE = /((?:tests|scripts|specs|supabase|src|app|shared|core|lib)\/[A-Za-z0-9_./-]+)/g;

for (const file of specs) {
  const rel = file.slice(ROOT.length + 1).replace(/\\/g, '/');
  const text = read(file);

  const fm = text.match(/^---\n([\s\S]*?)\n---/);
  if (!fm) { errors.push(`${rel}: missing YAML frontmatter.`); continue; }
  for (const key of REQUIRED_KEYS) {
    if (!new RegExp(`^${key}:`, 'm').test(fm[1])) {
      errors.push(`${rel}: frontmatter missing "${key}".`);
    }
  }
  const id = (fm[1].match(/^id:\s*(\S+)/m) || [])[1];
  if (id) {
    if (ids.has(id)) errors.push(`${rel}: duplicate spec id "${id}" also used by ${ids.get(id)}.`);
    ids.set(id, rel);
  }
  const version = (fm[1].match(/^version:\s*(\S+)/m) || [])[1];
  if (version && !/^\d+\.\d+\.\d+$/.test(version)) errors.push(`${rel}: version "${version}" is not semver (expected x.y.z).`);
  const status = (fm[1].match(/^status:\s*(\S+)/m) || [])[1];
  if (status && status !== 'approved') {
    const msg = `${rel}: status is "${status}" (not approved).`;
    (strict ? errors : warnings).push(msg);
  }

  const ver = text.match(/##\s*Verification([\s\S]*?)(\n##\s|\s*$)/);
  if (!ver) { errors.push(`${rel}: missing "## Verification" section.`); continue; }
  const realRefs = [...ver[1].matchAll(PATH_RE)].map((m) => m[1]).filter((r) => existsSync(join(ROOT, r)));
  if (realRefs.length === 0) {
    errors.push(`${rel}: Verification names no existing file (a spec untied to a real test is how drift slips in).`);
  }
}

for (const file of specs) {
  const rel = file.slice(ROOT.length + 1).replace(/\\/g, '/');
  const fm = read(file).match(/^---\n([\s\S]*?)\n---/);
  if (!fm) continue;
  const depends = (fm[1].match(/^depends_on:\s*\[([^\]]*)\]/m) || [])[1];
  if (!depends) continue;
  for (const dep of depends.split(',').map((v) => v.trim()).filter(Boolean)) {
    if (!ids.has(dep)) errors.push(`${rel}: depends_on unknown spec id "${dep}".`);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PROJECT-SPECIFIC DRIFT CHECKS — add yours below (schema↔code, naming, etc.).
// ─────────────────────────────────────────────────────────────────────────────

// Library mirrors: config/ is the editable source; src/fit_strong/data/ is the
// install-safe package copy. Enforce parsed content identity so formatting/EOL never
// false-fails, but real data drift is blocked.
for (const name of ['food_db.json', 'supplement_db.json', 'combination_rules.json']) {
  const srcDb = join(ROOT, 'config', name);
  const pkgDb = join(ROOT, 'src', 'fit_strong', 'data', name);
  if (existsSync(srcDb) && existsSync(pkgDb)) {
    const norm = (p) => JSON.stringify(JSON.parse(read(p)));
    try {
      if (norm(srcDb) !== norm(pkgDb)) {
        errors.push(`Library drift: config/${name} and src/fit_strong/data/${name} differ. config/ is the source.`);
      }
    } catch (e) {
      errors.push(`Library JSON parse error in ${name}: ${e.message}`);
    }
  } else if (existsSync(srcDb) !== existsSync(pkgDb)) {
    errors.push(`Library mirror incomplete for ${name}: config/ and package data must both exist.`);
  }
}

for (const w of warnings) console.warn(`⚠️  ${w}`);
if (errors.length) {
  for (const e of errors) console.error(`❌ ${e}`);
  console.error(`\nBOB validate FAILED — ${errors.length} error(s).`);
  process.exit(1);
}
console.log(`✅ BOB validate passed — ${specs.length} spec(s), constitution present${warnings.length ? `, ${warnings.length} warning(s)` : ''}.`);
