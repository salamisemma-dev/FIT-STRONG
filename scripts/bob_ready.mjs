#!/usr/bin/env node
import { spawnSync } from 'node:child_process';

const root = process.argv[2] ?? '.';
const commands = [
  ['node', ['scripts/bob_validate.mjs', '--strict', root]],
  ['python', ['-m', 'unittest', 'discover', '-s', 'tests']],
];

for (const [cmd, args] of commands) {
  const result = spawnSync(cmd, args, { cwd: root, stdio: 'inherit' });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
console.log('✅ BOB ready passed.');
