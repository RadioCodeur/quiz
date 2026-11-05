// Optional launcher for Node installations that do not put npm on PATH.
import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { execFileSync, spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = fileURLToPath(new URL('../', import.meta.url));
process.chdir(root);
const npm = path.join(root, '.tools/package/bin/npm-cli.js');
if (!existsSync(npm)) {
  console.log('Préparation locale de npm…');
  await mkdir('.tools', { recursive:true });
  const metadata = await (await fetch('https://registry.npmjs.org/npm/latest')).json();
  const response = await fetch(metadata.dist.tarball);
  if (!response.ok) throw new Error('Impossible de télécharger npm.');
  await writeFile('.tools/npm.tgz', Buffer.from(await response.arrayBuffer()));
  execFileSync('tar', ['-xzf', '.tools/npm.tgz', '-C', '.tools'], { stdio:'inherit' });
}
const env = { ...process.env, PATH: `${path.dirname(process.execPath)}${path.delimiter}${process.env.PATH}` };
if (!existsSync('node_modules/vite/package.json')) execFileSync(process.execPath,[npm,'ci'],{ stdio:'inherit',env });
const child = spawn(process.execPath,[npm,'run',process.argv[2] ?? 'dev',...process.argv.slice(3)],{ stdio:'inherit',env });
child.on('exit', code => process.exit(code ?? 1));
