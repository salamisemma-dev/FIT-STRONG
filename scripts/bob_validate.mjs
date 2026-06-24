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

const REQUIRED_KEYS = ['id', 'type', 'version', 'status', 'owner'];
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
  const status = (fm[1].match(/^status:\s*(\S+)/m) || [])[1];
  if (status && status !== 'approved') warnings.push(`${rel}: status is "${status}" (not approved).`);

  const ver = text.match(/##\s*Verification([\s\S]*?)(\n##\s|\s*$)/);
  if (!ver) { errors.push(`${rel}: missing "## Verification" section.`); continue; }
  const realRefs = [...ver[1].matchAll(PATH_RE)].map((m) => m[1]).filter((r) => existsSync(join(ROOT, r)));
  if (realRefs.length === 0) {
    errors.push(`${rel}: Verification names no existing file (a spec untied to a real test is how drift slips in).`);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PROJECT-SPECIFIC DRIFT CHECKS — add yours below (schema↔code, naming, etc.).
// Example pattern (uncomment + adapt):
//   const dream = existsSync(join(ROOT,'src/cron/nightlyDream.ts')) && read(join(ROOT,'src/cron/nightlyDream.ts'));
//   if (dream) { /* assert columns/invariants */ }
// ─────────────────────────────────────────────────────────────────────────────

for (const w of warnings) console.warn(`⚠️  ${w}`);
if (errors.length) {
  for (const e of errors) console.error(`❌ ${e}`);
  console.error(`\nBOB validate FAILED — ${errors.length} error(s).`);
  process.exit(1);
}
console.log(`✅ BOB validate passed — ${specs.length} spec(s), constitution present${warnings.length ? `, ${warnings.length} warning(s)` : ''}.`);
