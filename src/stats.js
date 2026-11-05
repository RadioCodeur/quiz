export function calculateStats(session, bank) {
  const byId = new Map(bank.map(q => [q.id, q]));
  const themes = {};
  let correct = 0, total = 0;
  for (const id of session.questionIds) {
    const q = byId.get(id);
    if (!q || session.answers[id] === undefined) continue;
    const success = session.answers[id] === q.correctOptionId;
    total++;
    correct += Number(success);
    for (const theme of q.themes) {
      themes[theme] ??= { correct: 0, total: 0, percent: 0 };
      themes[theme].total++;
      themes[theme].correct += Number(success);
    }
  }
  for (const value of Object.values(themes)) value.percent = Math.round(100 * value.correct / value.total);
  return { correct, total, percent: total ? Math.round(100 * correct / total) : 0, themes };
}
