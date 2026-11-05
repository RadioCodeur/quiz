import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { readBank } from './read-bank.mjs';

export function validateBank({ bank, themes, sources }) {
  const quotas = { 'python-scientifique': 20, pytorch: 50, 'audio-signal': 30, 'audio-ml': 30, 'generation-controle': 40, 'evaluation-recherche': 30 };
  assert.equal(bank.length, 200, 'La banque doit contenir exactement 200 questions');
  assert.equal(new Set(bank.map(q => q.id)).size, 200, 'Les identifiants doivent être uniques');
  assert.deepEqual(new Set(themes.map(t => t.id)), new Set(Object.keys(quotas)), 'Registre des thèmes');
  const refs = new Set(sources.map(s => s.id));
  assert.equal(refs.size, sources.length, 'Identifiants de sources uniques');
  for (const s of sources) {
    assert.ok(s.id && s.title && /^https:\/\//.test(s.url), `Référence invalide : ${s.id}`);
    assert.match(s.accessed, /^\d{4}-\d{2}-\d{2}$/, `Date de consultation : ${s.id}`);
  }
  const counts = {}, levels = {};
  for (const q of bank) {
    const check = (value, message) => assert.ok(value, `${q.id}: ${message}`);
    check(typeof q.id === 'string' && q.id.trim(), 'ID non vide');
    check(quotas[q.primaryTheme], 'thème principal valide');
    check(Array.isArray(q.themes) && q.themes.includes(q.primaryTheme), 'thème principal inclus');
    check(new Set(q.themes).size === q.themes.length && q.themes.every(t => quotas[t]), 'étiquettes valides et uniques');
    check(['fondamental', 'intermediaire', 'avance'].includes(q.difficulty), 'difficulté valide');
    check(typeof q.prompt === 'string' && q.prompt.trim(), 'énoncé non vide');
    check(q.code === undefined || typeof q.code === 'string', 'code textuel');
    check(Array.isArray(q.options) && q.options.length === 4, 'quatre options');
    check(new Set(q.options.map(o => o.id)).size === 4, 'IDs des options distincts');
    check(new Set(q.options.map(o => o.text.trim())).size === 4, 'textes des options distincts');
    check(q.options.every(o => typeof o.id === 'string' && o.id && typeof o.text === 'string' && o.text.trim()), 'options complètes');
    check(q.options.some(o => o.id === q.correctOptionId), 'bonne réponse existante');
    check(typeof q.explanation === 'string' && q.explanation.trim().length > 30, 'explication spécifique non vide');
    check(Array.isArray(q.sourceIds) && q.sourceIds.length && q.sourceIds.every(s => refs.has(s)), 'références existantes');
    counts[q.primaryTheme] = (counts[q.primaryTheme] ?? 0) + 1;
    levels[q.difficulty] = (levels[q.difficulty] ?? 0) + 1;
  }
  assert.deepEqual(counts, quotas, 'Quotas par thème principal');
  assert.ok(bank.filter(q => q.code?.trim()).length >= 60, 'Au moins 60 questions avec code');
  assert.deepEqual(levels, { fondamental: 60, intermediaire: 100, avance: 40 }, 'Répartition des difficultés');
  return { total: bank.length, code: bank.filter(q => q.code?.trim()).length, counts, levels, sources: sources.length };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const result = validateBank(await readBank());
  console.log(JSON.stringify(result, null, 2));
}
