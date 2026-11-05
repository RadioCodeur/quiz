import test from 'node:test';
import assert from 'node:assert/strict';
import { readBank } from '../scripts/read-bank.mjs';
import { validateBank } from '../scripts/validate-bank.mjs';
import { filterQuestions, shuffle, availableCounts, defaultCount, createSession, prepareOptions, answerQuestion, advance, retryQuestions } from '../src/quiz.js';
import { calculateStats } from '../src/stats.js';
import { bankSignature, createStorage, validateSession, STORAGE_KEY } from '../src/storage.js';
const data = await readBank();
const { bank } = data;
const sample = (n = 10) => prepareOptions(createSession(bank, n), bank);
const memory = () => { const map = new Map(); return { getItem: key => map.get(key) ?? null, setItem: (key, value) => map.set(key, value), removeItem: key => map.delete(key) }; };

test('la banque complète respecte tous les quotas et le schéma', () => { assert.equal(validateBank(data).total, 200); });
test('le filtrage est une union sans doublons, y compris sur les questions multi-étiquettes', () => {
  const one = filterQuestions(bank, ['pytorch']);
  const two = filterQuestions(bank, ['audio-ml']);
  const union = filterQuestions(bank, ['pytorch', 'audio-ml']);
  assert.deepEqual(new Set(union.map(q => q.id)), new Set([...one, ...two].map(q => q.id)));
  assert.equal(new Set(union.map(q => q.id)).size, union.length);
  assert.deepEqual(filterQuestions(bank, []), []);
});
test('formats limités au stock et à 200 ; valeur par défaut', () => {
  assert.deepEqual(availableCounts(29), [10, 20]);
  assert.deepEqual(availableCounts(9), []);
  assert.equal(availableCounts(500).at(-1), 200);
  assert.equal(defaultCount(200), 50);
  assert.equal(defaultCount(29), 20);
  assert.equal(defaultCount(9), 0);
});
test('tirage exact sans remise sur plusieurs sessions', () => {
  for (let i = 0; i < 60; i++) {
    const s = sample(200);
    assert.equal(s.questionIds.length, 200);
    assert.equal(new Set(s.questionIds).size, 200);
  }
  assert.throws(() => createSession(bank, 201));
  assert.throws(() => createSession(bank, 0));
});
test('mélange sans mutation et préservation des réponses par ID', () => {
  const original = [1, 2, 3, 4];
  assert.deepEqual(shuffle(original, () => 0), [2, 3, 4, 1]);
  assert.deepEqual(original, [1, 2, 3, 4]);
  const s = sample(200);
  for (const q of bank) {
    assert.deepEqual(new Set(s.optionOrders[q.id]), new Set(q.options.map(o => o.id)));
    assert.ok(s.optionOrders[q.id].includes(q.correctOptionId));
  }
  assert.ok(bank.some(q => s.optionOrders[q.id].join() !== q.options.map(o => o.id).join()));
});
test('réponses validées une fois, refus des options invalides et passage protégé', () => {
  const s = sample(2), q = bank.find(q => q.id === s.questionIds[0]);
  assert.equal(advance(s), false);
  assert.equal(answerQuestion(s, q, 'inexistant'), false);
  assert.equal(answerQuestion(s, q, q.correctOptionId), true);
  assert.equal(answerQuestion(s, q, q.options.find(o => o.id !== q.correctOptionId).id), false);
  assert.equal(advance(s), true);
  assert.equal(s.answers[q.id], q.correctOptionId);
  const next = bank.find(q => q.id === s.questionIds[1]);
  answerQuestion(s, next, next.correctOptionId); advance(s);
  assert.equal(s.completed, true);
  assert.equal(answerQuestion(s, next, next.correctOptionId), false);
});
test('scores globaux uniques et attribution de chaque thème', () => {
  const qs = [{ id:'x', correctOptionId:'a', themes:['one','two'] }, { id:'y', correctOptionId:'b', themes:['two'] }];
  const result = calculateStats({ questionIds:['x','y'], answers:{x:'a',y:'a'} }, qs);
  assert.deepEqual(result, { correct:1,total:2,percent:50,themes:{one:{correct:1,total:1,percent:100},two:{correct:1,total:2,percent:50}} });
});
test('mode erreurs reprend exactement les erreurs, même une seule', () => {
  const s = sample(2), qs = s.questionIds.map(id => bank.find(q => q.id === id));
  answerQuestion(s, qs[0], qs[0].correctOptionId); advance(s);
  answerQuestion(s, qs[1], qs[1].options.find(o => o.id !== qs[1].correctOptionId).id); advance(s);
  const errors = retryQuestions(s, bank);
  assert.deepEqual(errors.map(q => q.id), [qs[1].id]);
  const retry = prepareOptions(createSession(errors, errors.length, { mode:'errors' }), bank);
  assert.equal(retry.questionIds.length, 1);
  assert.equal(retry.mode, 'errors');
});
test('session et ordre des choix conservés après sérialisation', () => {
  const mem = memory(), store = createStorage(() => mem), sig = bankSignature(bank), s = sample();
  const q = bank.find(q => q.id === s.questionIds[0]);
  answerQuestion(s,q,q.correctOptionId); store.saveSession(s,sig);
  assert.deepEqual(store.loadSession(bank,sig), {session:s,discarded:false});
});
test('stockage bloqué : pas de crash et session utilisable en mémoire', () => {
  const store = createStorage(() => { throw new Error('SecurityError'); });
  const s = sample(); store.saveSession(s,'x');
  assert.equal(store.available,false);
  assert.equal(store.loadSession(bank,'x').session,null);
  assert.equal(answerQuestion(s,bank.find(q => q.id === s.questionIds[0]),'a'),true);
});
test('JSON corrompu, banque changée et sessions incohérentes écartés', () => {
  const mem = memory(), store = createStorage(() => mem), sig = bankSignature(bank);
  mem.setItem(STORAGE_KEY,'{broken');
  assert.equal(store.loadSession(bank,sig).discarded,true);
  store.saveSession(sample(),'old-signature');
  assert.equal(store.loadSession(bank,sig).discarded,true);
  const s = sample();
  for (const mutate of [s => s.questionIds.push(s.questionIds[0]), s => s.optionOrders = null, s => s.index = -1, s => s.completed = true, s => s.answers.nope = 'a', s => s.questionIds[0] = 'removed', s => s.optionOrders[s.questionIds[0]] = ['a','a','c','d'], s => s.index = 1, s => s.answers[s.questionIds[1]] = 'a']) {
    const bad = structuredClone(s); mutate(bad); assert.equal(validateSession(bad,bank),false);
  }
});
test('la signature change si un contenu pédagogique change', () => {
  const copy = structuredClone(bank); copy[0].explanation += ' Modification.';
  assert.notEqual(bankSignature(copy),bankSignature(bank));
});
