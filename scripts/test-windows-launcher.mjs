import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

if (process.platform !== 'win32') {
  console.log('Test du lanceur réservé à Windows.');
  process.exit(0);
}

const root = fileURLToPath(new URL('../', import.meta.url));
const windows = process.env.SystemRoot ?? 'C:\\Windows';
const env = Object.fromEntries(Object.entries(process.env).filter(([key]) => key.toLowerCase() !== 'path'));
// Reproduce Explorer's environment: Codex's injected Node path is absent.
env.PATH = [path.join(windows, 'System32'), windows].join(';');
env.QUIZ_NO_OPEN = '1';
const child = spawn(path.join(windows, 'System32/cmd.exe'), ['/d', '/c', 'call Lancer.cmd --port 5191 --strictPort'], {
  cwd: root, env, windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'],
});
child.stdin.end();
let output = '';
let exited = false;
child.stdout.on('data', chunk => { output += chunk; });
child.stderr.on('data', chunk => { output += chunk; });
child.on('exit', () => { exited = true; });
child.on('error', error => { output += error.message; exited = true; });

try {
  let ready = false;
  for (let i = 0; i < 120; i++) {
    if (exited) throw new Error(`Le lanceur s'est arrêté :\n${output}`);
    try {
      const response = await fetch('http://127.0.0.1:5191', { signal: AbortSignal.timeout(500) });
      if (response.ok && output.includes('5191')) { ready = true; break; }
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  assert.ok(ready, `Le quiz n'a pas démarré :\n${output}`);
  const response = await fetch('http://127.0.0.1:5191');
  assert.ok((await response.text()).includes('À l’écoute'));
  const themes = await (await fetch('http://127.0.0.1:5191/data/themes.json')).json();
  const groups = await Promise.all(themes.map(async t => (await fetch(`http://127.0.0.1:5191/data/${t.file}`)).json()));
  assert.equal(groups.flat().length, 200);
  console.log('✓ Double-clic simulé sous Windows, sans Node dans le PATH : serveur démarré et 200 questions accessibles.');
} finally {
  if (!exited) {
    try { execFileSync(path.join(windows, 'System32/taskkill.exe'), ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore', windowsHide: true }); }
    catch { child.kill(); }
  }
}
