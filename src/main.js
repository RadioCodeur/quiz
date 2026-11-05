import './style.css';
import { loadBank } from './bank.js';
import { filterQuestions, availableCounts, defaultCount, createSession, prepareOptions, answerQuestion, advance, retryQuestions } from './quiz.js';
import { calculateStats } from './stats.js';
import { createStorage, bankSignature, STORAGE_KEY, SETTINGS_KEY } from './storage.js';

const root = document.querySelector('#app');
const storage = createStorage();
const escape = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const wave = `<div class="wave" aria-hidden="true">${[20,36,52,30,66,88,58,106,74,120,86,54,98,68,42,78,56,100,70,44,62,34,48,24,40,16].map((h, i) => `<i style="--h:${h}px;--i:${i}"></i>`).join('')}</div>`;
let bank, themes, sources, signature, session = null, discarded = false;
let selected = [], count = 50;

function themeLabel(id) { return themes.find(t => t.id === id)?.label ?? id; }
function sourceList(q) {
  return `<details class="sources"><summary>Consulter les références</summary><ul>${q.sourceIds.map(id => sources.find(s => s.id === id)).filter(Boolean).map(s => `<li><a href="${escape(s.url)}" target="_blank" rel="noopener noreferrer">${escape(s.title)} ↗</a></li>`).join('')}</ul></details>`;
}
function tags(q) { return q.themes.map(id => `<span class="tag">${escape(themeLabel(id))}</span>`).join(''); }
function code(q) { return q.code ? `<div class="code-label">PYTHON</div><pre><code>${escape(q.code)}</code></pre><p class="code-conventions">Imports usuels supposés : <code>torch</code> pour PyTorch, <code>np</code> pour NumPy. Le code est à lire, sans exécution.</p>` : ''; }
function focusMain() { root.focus({ preventScroll: true }); window.scrollTo({ top: 0, behavior: 'instant' }); }
function storageNotice() { return !storage.available ? '<p class="notice" role="status">Le stockage est indisponible. Votre session reste utilisable, mais ne sera pas conservée après fermeture ou rafraîchissement.</p>' : ''; }
function persist() { storage.saveSession(session, signature); }
function saveSettings() { storage.write(SETTINGS_KEY, { selected, count }); }

function showConfig() {
  const stock = filterQuestions(bank, selected).length;
  const options = availableCounts(stock);
  if (!options.includes(count)) count = defaultCount(stock);
  root.innerHTML = `
    <section class="hero"><div><p class="eyebrow"><span class="small-dot"></span> VOTRE PROCHAINE IDÉE COMMENCE ICI</p><h1>L’IA audio,<br><span>une question à la fois.</span></h1><p class="hero-description">Du tenseur au son. Révisez les concepts, lisez du code et affinez votre raisonnement, à votre rythme.</p><div class="hero-facts"><span><strong>200</strong> questions expliquées</span><span><strong>6</strong> terrains d’exploration</span></div></div><div class="hero-art">${wave}<span>APPRENDRE À MIEUX ENTENDRE</span></div></section>
    ${storageNotice()}${discarded ? '<p class="notice" role="status">La sauvegarde était invalide ou la banque a changé. Une nouvelle session peut être lancée.</p>' : ''}
    ${session ? `<aside class="resume"><div><strong>${session.completed ? 'Votre dernier bilan est disponible' : 'Une session vous attend'}</strong><p>${session.questionIds.length} questions · ${Object.keys(session.answers).length} réponses enregistrées</p></div><button id="resume" class="button secondary">${session.completed ? 'Revoir mon bilan' : 'Reprendre la session'} <span aria-hidden="true">↗</span></button></aside>` : ''}
    <section class="configuration" aria-labelledby="config-title"><div class="config-main"><div class="section-heading"><div><p class="eyebrow">01 / LES THÈMES</p><h2 id="config-title">Composez votre session</h2></div><label class="select-all"><input type="checkbox" id="all-themes" ${selected.length === themes.length ? 'checked' : ''}> Tout sélectionner</label></div><p class="section-intro">Choisissez un thème ou croisez les disciplines.</p><fieldset class="theme-grid"><legend class="sr-only">Thèmes à réviser</legend>${themes.map(t => `<label class="theme-card ${selected.includes(t.id) ? 'is-selected' : ''}"><div class="theme-top"><span class="theme-number">${t.symbol}</span><input type="checkbox" name="theme" value="${t.id}" ${selected.includes(t.id) ? 'checked' : ''} aria-label="${escape(t.label)}"></div><strong>${escape(t.label)}</strong><span class="theme-description">${escape(t.description)}</span><span class="theme-count">${filterQuestions(bank, [t.id]).length} questions</span></label>`).join('')}</fieldset></div>
    <aside class="session-card"><p class="eyebrow">02 / LE FORMAT</p><h2>Un moment pour <br>progresser.</h2><label class="field-label" for="question-count">Nombre de questions</label><div class="select-wrap"><select id="question-count" ${!options.length ? 'disabled' : ''}>${options.length ? options.map(n => `<option value="${n}" ${n === count ? 'selected' : ''}>${n} questions</option>`).join('') : '<option>Aucune session disponible</option>'}</select></div><p class="available"><span class="small-dot"></span><strong id="available-count">${stock}</strong> questions uniques disponibles</p><div class="session-divider"></div><ul class="session-promises"><li><span aria-hidden="true">✓</span> 4 choix, une seule bonne réponse</li><li><span aria-hidden="true">✓</span> Une explication à chaque réponse</li><li><span aria-hidden="true">✓</span> Sans chrono, à votre rythme</li></ul>${stock < 10 ? `<p class="notice" role="status">${!selected.length ? 'Sélectionnez au moins un thème pour commencer.' : 'Il faut au moins 10 questions disponibles.'}</p>` : ''}<button id="start" class="button primary start-button" ${stock < 10 ? 'disabled' : ''}>Commencer la session <span aria-hidden="true">→</span></button><p class="local-note">Votre session se sauvegarde sur cet appareil.</p></aside></section>
    <section class="bottom-note"><span aria-hidden="true">↳</span><p>Comprendre, puis pratiquer.<br><span>Ici, on lit et on raisonne. L’écriture de code se pratique séparément.</span></p></section><p class="independence">Questions originales de préparation à la recherche en IA audio. Aucune affiliation avec l’IRCAM ; ces questions ne proviennent pas de ses entretiens.</p>`;
  root.querySelector('#all-themes').indeterminate = selected.length > 0 && selected.length < themes.length;
  root.querySelector('#all-themes').addEventListener('change', e => { selected = e.target.checked ? themes.map(t => t.id) : []; saveSettings(); showConfig(); root.querySelector('#all-themes').focus(); });
  root.querySelectorAll('[name="theme"]').forEach(input => input.addEventListener('change', () => {
    selected = [...root.querySelectorAll('[name="theme"]:checked')].map(el => el.value);
    saveSettings(); showConfig(); root.querySelector(`[value="${input.value}"]`).focus();
  }));
  root.querySelector('#question-count').addEventListener('change', e => { count = Number(e.target.value); saveSettings(); });
  root.querySelector('#resume')?.addEventListener('click', () => { session.completed ? showResults() : showQuestion(); focusMain(); });
  root.querySelector('#start').addEventListener('click', () => {
    if (session && !session.completed && !window.confirm('Remplacer la session en cours ? Votre progression actuelle sera perdue.')) return;
    launch(filterQuestions(bank, selected), count);
  });
}

function launch(questions, n, mode = 'normal') {
  session = prepareOptions(createSession(questions, n, { mode }), bank);
  persist(); showQuestion(); focusMain();
}

function showQuestion() {
  const q = bank.find(q => q.id === session.questionIds[session.index]);
  const chosen = session.answers[q.id];
  const answered = chosen !== undefined;
  const correct = chosen === q.correctOptionId;
  const last = session.index === session.questionIds.length - 1;
  root.innerHTML = `<section class="quiz-shell"><div class="quiz-nav"><span class="eyebrow">${session.mode === 'errors' ? 'REPRENDRE SES ERREURS' : 'UNE IDÉE À LA FOIS'}</span><button class="text-button" id="abandon">Quitter la session <span aria-hidden="true">↗</span></button></div><div class="progress-heading"><p>Question <strong>${session.index + 1}</strong> / ${session.questionIds.length}</p><span>${Object.keys(session.answers).length} réponse${Object.keys(session.answers).length === 1 ? '' : 's'} validée${Object.keys(session.answers).length === 1 ? '' : 's'}</span></div><progress max="${session.questionIds.length}" value="${Object.keys(session.answers).length}" aria-label="Questions validées"></progress>${storageNotice()}<article class="question-card"><div class="question-meta">${tags(q)}<span class="difficulty">${({fondamental:'Fondamental',intermediaire:'Intermédiaire',avance:'Avancé'})[q.difficulty]}</span></div><h1 class="question-title">${escape(q.prompt)}</h1>${code(q)}<p class="choice-hint">Choisissez une réponse. Elle sera validée immédiatement.</p><div class="answers">${session.optionOrders[q.id].map((id, i) => {
    const option = q.options.find(o => o.id === id);
    const isCorrect = answered && id === q.correctOptionId;
    const isWrong = answered && id === chosen && !correct;
    return `<button type="button" class="answer ${isCorrect ? 'correct' : ''} ${isWrong ? 'wrong' : ''}" data-option="${escape(id)}" ${answered ? 'disabled' : ''}><span class="answer-letter" aria-hidden="true">${String.fromCharCode(65 + i)}</span><span class="answer-content">${escape(option.text)}${isCorrect ? '<strong class="answer-state">✓ Bonne réponse</strong>' : ''}${isWrong ? '<strong class="answer-state">× Votre réponse</strong>' : ''}</span></button>`;
  }).join('')}</div>${answered ? `<section class="feedback ${correct ? 'success' : 'mistake'}" role="status" tabindex="-1"><h2>${correct ? '✓ Bien vu.' : '↳ Une occasion de comprendre.'}</h2><p>${escape(q.explanation)}</p>${sourceList(q)}</section><div class="next-row"><button class="button primary" id="next">${last ? 'Voir mon bilan' : 'Question suivante'} <span aria-hidden="true">→</span></button></div>` : ''}</article></section>`;
  root.querySelectorAll('[data-option]').forEach(button => button.addEventListener('click', () => {
    if (answerQuestion(session, q, button.dataset.option)) { persist(); showQuestion(); root.querySelector('.feedback').focus({ preventScroll: true }); }
  }));
  root.querySelector('#next')?.addEventListener('click', () => { if (advance(session)) { persist(); session.completed ? showResults() : showQuestion(); focusMain(); } });
  root.querySelector('#abandon').addEventListener('click', () => {
    if (window.confirm('Abandonner cette session ? Ses réponses seront effacées.')) {
      session = null; storage.remove(STORAGE_KEY); showConfig(); focusMain();
    }
  });
}

function showResults() {
  const stats = calculateStats(session, bank);
  const errors = retryQuestions(session, bank);
  const ranked = Object.entries(stats.themes).sort((a, b) => b[1].percent - a[1].percent || b[1].total - a[1].total);
  const bestPercent = ranked[0]?.[1].percent;
  const worstPercent = ranked.at(-1)?.[1].percent;
  const best = ranked.filter(([, t]) => t.percent === bestPercent).map(([id]) => themeLabel(id)).join(', ');
  const worst = ranked.filter(([, t]) => t.percent === worstPercent).map(([id]) => themeLabel(id)).join(', ');
  root.innerHTML = `<section class="results-shell"><p class="eyebrow">SESSION TERMINÉE / PLACE AU RECUL</p><h1>Une idée plus claire.</h1><p class="result-intro">Chaque réponse est un point de départ pour la suite.</p>${storageNotice()}<section class="score-card"><div class="score-number">${stats.percent}<span>%</span></div><div><h2>${stats.correct} bonne${stats.correct === 1 ? '' : 's'} réponse${stats.correct === 1 ? '' : 's'} sur ${stats.total}</h2><p>Le résultat de cette session, à votre rythme.</p></div><span class="score-decoration" aria-hidden="true">↗</span></section><div class="results-actions"><button class="button primary" id="new-session">Nouvelle session <span aria-hidden="true">→</span></button><button class="button secondary" id="retry" ${!errors.length ? 'disabled' : ''}>Refaire mes erreurs (${errors.length})</button></div><section class="result-section"><p class="eyebrow">LES THÈMES / EN DÉTAIL</p><h2>Vos repères pour la suite</h2><p class="muted">Une question peut compter dans plusieurs thèmes. Les nombres par thème ne s’additionnent donc pas au total.</p><div class="theme-results">${themes.filter(t => stats.themes[t.id]).map(t => {
    const s = stats.themes[t.id];
    return `<div class="theme-result"><div><strong>${escape(t.label)}</strong><span>${s.correct} / ${s.total} · ${s.percent}%</span></div><progress value="${s.correct}" max="${s.total}" aria-label="${escape(t.label)} : ${s.percent}%"></progress>${s.total < 5 ? '<small>Peu de questions : résultat indicatif.</small>' : ''}</div>`;
  }).join('')}</div><div class="insights">${bestPercent === worstPercent ? `<p><strong>Résultats homogènes.</strong> Vos thèmes ont le même pourcentage sur cette session.</p>` : `<p><strong>Les mieux réussis ·</strong> ${escape(best)} (${bestPercent}%).</p><p><strong>À retravailler ·</strong> ${escape(worst)} (${worstPercent}%).</p>`}<p class="muted">Ces repères concernent cette session. Ils ne mesurent pas définitivement votre niveau ; sur très peu de questions, ils restent indicatifs.</p></div></section><section class="result-section"><p class="eyebrow">COMPRENDRE / PUIS RÉESSAYER</p><h2>Le carnet des erreurs <span class="error-count">${errors.length}</span></h2>${errors.length ? errors.map((q, i) => `<details class="error-item"><summary><span class="error-index">${String(i + 1).padStart(2, '0')}</span><span>${escape(q.prompt)}</span><span class="detail-plus" aria-hidden="true">+</span></summary><div class="error-body"><div class="question-meta">${tags(q)}</div>${code(q)}<p class="selected-error"><strong>× Votre réponse :</strong> ${escape(q.options.find(o => o.id === session.answers[q.id]).text)}</p><p class="selected-correct"><strong>✓ Bonne réponse :</strong> ${escape(q.options.find(o => o.id === q.correctOptionId).text)}</p><p>${escape(q.explanation)}</p>${sourceList(q)}</div></details>`).join('') : '<div class="empty-errors"><strong>✓ Tout juste pour cette session.</strong><p>Aucune erreur à revoir. Vous pouvez explorer un autre thème.</p></div>'}</section></section>`;
  root.querySelector('#new-session').addEventListener('click', () => { session = null; storage.remove(STORAGE_KEY); showConfig(); focusMain(); });
  root.querySelector('#retry').addEventListener('click', () => { if (errors.length) launch(errors, errors.length, 'errors'); });
}

async function init() {
  try {
    ({ bank, themes, sources } = await loadBank());
    signature = bankSignature(bank);
    const settings = storage.read(SETTINGS_KEY);
    selected = Array.isArray(settings?.selected) ? [...new Set(settings.selected.filter(id => themes.some(t => t.id === id)))] : themes.map(t => t.id);
    count = Number.isInteger(settings?.count) ? settings.count : 50;
    ({ session, discarded } = storage.loadSession(bank, signature));
    // Restore the exact question and correction, including shuffled options.
    if (session) session.completed ? showResults() : showQuestion();
    else showConfig();
  } catch (error) {
    console.error(error);
    root.innerHTML = '<section class="load-error"><h1>Les questions n’ont pas pu être chargées.</h1><p>Vérifiez que l’application est lancée avec le serveur local et que les fichiers de données sont présents.</p><button class="button primary" id="reload">Réessayer</button></section>';
    root.querySelector('#reload').addEventListener('click', () => location.reload());
  }
}
init();
