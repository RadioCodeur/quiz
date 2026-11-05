import { readFile } from 'node:fs/promises';
const dir = new URL('../public/data/', import.meta.url);
export const readJSON = async file => JSON.parse(await readFile(new URL(file, dir), 'utf8'));
export async function readBank() {
  const themes = await readJSON('themes.json');
  const bank = (await Promise.all(themes.map(t => readJSON(t.file)))).flat();
  const sources = (await Promise.all(['sources-python-pytorch.json', 'sources-audio.json', 'sources-generation-research.json'].map(readJSON))).flat();
  return { themes, bank, sources };
}
