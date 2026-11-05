export function shuffle(items, random = Math.random) {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

export function filterQuestions(bank, themes) {
  const selected = new Set(themes);
  return bank.filter(q => q.themes.some(t => selected.has(t)));
}

export function availableCounts(stock) {
  return Array.from({ length: Math.floor(Math.min(stock, 200) / 10) }, (_, i) => (i + 1) * 10);
}

export function defaultCount(stock) {
  return Math.min(50, availableCounts(stock).at(-1) ?? 0);
}

export function createSession(questions, count, { mode = 'normal', random = Math.random } = {}) {
  const unique = [...new Map(questions.map(q => [q.id, q])).values()];
  if (!Number.isInteger(count) || count < 1 || count > unique.length) throw new Error('Nombre de questions invalide.');
  // A shuffled stock naturally mixes themes without imposing equal quotas.
  return {
    version: 1,
    mode,
    questionIds: shuffle(unique, random).slice(0, count).map(q => q.id),
    optionOrders: {},
    answers: {},
    index: 0,
    completed: false,
    startedAt: new Date().toISOString(),
  };
}

export function prepareOptions(session, bank, random = Math.random) {
  const byId = new Map(bank.map(q => [q.id, q]));
  for (const id of session.questionIds) session.optionOrders[id] = shuffle(byId.get(id).options.map(o => o.id), random);
  return session;
}

export function answerQuestion(session, question, optionId) {
  if (session.completed || session.questionIds[session.index] !== question.id || session.answers[question.id] !== undefined) return false;
  if (!question.options.some(o => o.id === optionId)) return false;
  session.answers[question.id] = optionId;
  return true;
}

export function advance(session) {
  if (session.answers[session.questionIds[session.index]] === undefined) return false;
  if (session.index === session.questionIds.length - 1) session.completed = true;
  else session.index++;
  return true;
}

export function retryQuestions(session, bank) {
  const byId = new Map(bank.map(q => [q.id, q]));
  return session.questionIds.map(id => byId.get(id)).filter(q => q && session.answers[q.id] !== undefined && session.answers[q.id] !== q.correctOptionId);
}
