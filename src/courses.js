import './style.css';
import './courses.css';
import './learning.css';
import './course-media.css';
import './tensor-labs.css';
import { loadBank } from './bank.js';
import { createStorage } from './storage.js';
import { COURSE_ORDER, COURSE_STORAGE_KEY, courseHref, buildCoverage, chapterMinutes, normalizeProgress, setChapterRead, resolveChapter, courseStage, mergeCourseReferences, chapterNavigation, notebookLinks,checkpointSignature,setChapterReview } from './course-model.js';
import { renderFigure } from './course-figures.js';
import { renderVisual, renderPlot, renderWalkthrough, attachWalkthroughs, renderCheckpoint, attachCheckpoint, renderFirstExample, renderLessonList,renderCodePreparation } from './learning-blocks.js';
import {renderTensorLab,attachTensorLabs} from './tensor-labs.js';

import { renderIllustration, renderAudioLab, renderAnalysisImage, attachAudioLabs } from './course-media.js';
import {QUICK_CHAPTERS,REVISION_WEEKS,quickChapter} from './revision-path.js';

const root = document.querySelector('#app');
const storage = createStorage();
const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' })[c]);
const portrait = `${import.meta.env.BASE_URL}images/professeur-squoinks.png`;
let courses = [], themes = [], sources = [], bank = [], progress, coverage, pedagogy, audioMedia, illustrations;
let serial = 0;
let activeReadKey=null,scrollWriteTimer;
const name = id => courses.find(course=>course.themeId===id)?.label ?? themes.find(t => t.id === id)?.label ?? id;
const readKey = (course, chapter) => `${course.themeId}/${chapter.id}`;
const minutes = course => course.chapters.reduce((sum, ch) => sum + chapterMinutes(ch), 0);
const readCount = course => course.chapters.filter(ch => progress.completed.includes(readKey(course,ch))).length;
function save() { storage.write(COURSE_STORAGE_KEY, progress); }
function rememberReading(){
  if(!activeReadKey||!progress?.chapterStates?.[activeReadKey])return;
  progress.chapterStates[activeReadKey].scrollY=window.scrollY;save();
}
function preserveReadingPosition(change){
  const anchor=[...root.querySelectorAll('.lesson-body p,.lesson-body h3,.walk-code-line,.lesson-body img')].find(element=>element.getBoundingClientRect().bottom>80&&element.getBoundingClientRect().width>0);
  const before=anchor?.getBoundingClientRect().top;
  change();
  requestAnimationFrame(()=>{if(anchor)window.scrollBy(0,anchor.getBoundingClientRect().top-before);rememberReading();});
}
function storageNotice() { return storage.available ? '' : '<p class="notice" role="status">Le stockage est indisponible. Vous pouvez lire tous les cours ; les repères de lecture ne seront pas conservés après fermeture.</p>'; }
function focusReading() { root.focus({ preventScroll:true }); window.scrollTo({ top:0, behavior:'instant' }); }
function applyPreferences() {
  document.body.classList.toggle('reading-focus', progress.readingMode);
  document.body.classList.toggle('large-reading-text', progress.largeText);
}
function references(ids) {
  return `<details class="lesson-references"><summary>Pour aller à la source <span>Documentation et publications</span></summary><ul>${ids.map(id => sources.find(s => s.id === id)).filter(Boolean).map(s => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)} ↗</a></li>`).join('')}</ul></details>`;
}
function renderBlock(block) {
  if(block.disclosure)return `<details class="optional-example"><summary>${esc(block.caption??block.title??'Ouvrir ce complément')}</summary>${renderBlock({...block,disclosure:false,...(block.type==='code'?{caption:''}:{})})}</details>`;
  if(block.type==='list'&&block.role==='pitch-template')return `<section class="pitch-template"><h3>${esc(block.title)}</h3><p>Vos notes sont conservées sur cet appareil. Remplacez les hypothèses du modèle par vos choix et votre expérience réels.</p>${block.items.map((item,index)=>`<label for="pitch-${index}">${esc(item)}<textarea id="pitch-${index}" data-pitch-field="${index}" rows="4" maxlength="5000"></textarea></label>`).join('')}<p class="pitch-save-status" role="status"></p></section>`;
  if(block.type==='illustration')return renderIllustration(block,illustrations,import.meta.env.BASE_URL);
  if(block.type==='audio-lab')return renderAudioLab(block,audioMedia,++serial,import.meta.env.BASE_URL);
  if(block.type==='analysis-image')return renderAnalysisImage(block,audioMedia,import.meta.env.BASE_URL);
  if(block.type==='paragraph') return `<p>${esc(block.text)}</p>`;
  if(block.type==='heading') return `<h3>${esc(block.text)}</h3>`;
  if(block.type==='list') return renderLessonList(block);
  if(block.type==='code') return `${renderCodePreparation(block,import.meta.env.BASE_URL)}<figure class="lesson-code"><div class="code-label">${esc(block.language ?? 'python')} · EXEMPLE COMMENTÉ <button type="button" class="copy-course-code">Copier le code</button></div><pre><code>${esc(block.code)}</code></pre>${block.caption?`<figcaption>${esc(block.caption)}</figcaption>`:''}</figure>`;
  if(block.type==='callout') return `<aside class="lesson-callout ${esc(block.tone)}"><span class="callout-symbol" aria-hidden="true">${block.tone==='analogy'?'↔':block.tone==='pitfall'?'!':'↳'}</span><div><h3>${esc(block.label)}</h3><p>${esc(block.text)}</p></div></aside>`;
  if(block.type==='example') return `<section class="real-example"><p class="eyebrow">UNE UTILISATION CONCRÈTE</p><h3>${esc(block.title)}</h3><p>${esc(block.text)}</p></section>`;
  if(block.type==='figure') return renderFigure(block.kind,block.caption,++serial);
  if(block.type==='visual') return renderVisual(block);
  if(block.type==='plot') return renderPlot(block,++serial);
  if(block.type==='walkthrough') return renderWalkthrough(block,++serial,import.meta.env.BASE_URL);
  if(block.type==='tensor-lab')return renderTensorLab(block,++serial);
  if(block.type==='first-example') return renderFirstExample(block,import.meta.env.BASE_URL);
  return '';
}

function renderLessonBody(chapter) {
  let answerShown=false;
  return chapter.blocks.map((block,index)=>{
    if(block.role!=='oral-answer')return renderBlock(block)+(index===0?renderNotebook(chapter):'');
    if(answerShown)return '';
    answerShown=true;
    const isPitch=chapter.oral.kind==='pitch';
    const scaffold=chapter.oral.scaffold;
    const hints=scaffold?`<section class="oral-scaffold"><p><strong>Ce que cette question permet de vérifier.</strong> ${esc(scaffold.evaluates)}</p><ol>${scaffold.hints.map((hint,i)=>`<li><details><summary>Voir une piste ${i+1}</summary><p>${esc(hint)}</p></details></li>`).join('')}</ol><p>${esc(scaffold.personalize)}</p></section>`:'';
    return `${hints}<details class="oral-model"><summary>${isPitch?'Voir un pitch hypothétique':'Voir un exemple de réponse'}</summary><p class="oral-duration">${chapter.oral.answerWords} mots · ${isPitch?'environ deux minutes':'environ 60 à 90 secondes'}, selon votre débit. Reformulez à votre rythme.</p>${chapter.blocks.filter(item=>item.role==='oral-answer').map(renderBlock).join('')}</details>`;
  }).join('');
}

function renderGlobalRoadmap() {
  return `<section class="global-learning-goal"><p class="eyebrow">LE FIL ROUGE DU PARCOURS</p><h2>Transformer des sons en données, puis en décisions et en créations.</h2><p>Au départ, vous avez des enregistrements. À l’arrivée, vous savez expliquer comment les préparer, apprendre un modèle, contrôler un générateur et vérifier ce qu’il apporte. Chaque cours construit une partie de cette chaîne.</p><ol>${courses.map((course,index)=>`<li><a href="${courseHref(course.themeId)}"><span>${String(index+1).padStart(2,'0')}</span>${esc(name(course.themeId))}</a></li>`).join('')}</ol></section>`;
}

function quickBadge(themeId,chapterId) {
  return quickChapter(themeId,chapterId)?'<small class="quick-label">À survoler si acquis</small>':'';
}
function renderQuickNote(course,chapter) {
  const quick=quickChapter(course.themeId,chapter.id);
  const note=quick?`<aside class="quick-chapter-note"><strong>Parcours rapide · À survoler si acquis</strong><p>${esc(quick.condition)} Essayez le repère du chapitre ; revenez à l’exemple si votre explication hésite.</p></aside>`:'';
  return note+(chapter.lengthJustification?`<aside class="quick-chapter-note"><strong>Une lecture à répartir en plusieurs pauses</strong><p>${esc(chapter.lengthJustification)}</p></aside>`:'');
}
function renderRevisionPath() {
  const find=(themeId,chapterId)=>courses.find(course=>course.themeId===themeId).chapters.find(chapter=>chapter.id===chapterId);
  return `<details class="revision-path" id="parcours-rapide"><summary><strong>Déjà à l’aise avec le mel et les autoencodeurs ?</strong><span>Parcours rapide et révision sur quatre semaines</span></summary><p>Nous donnons la priorité à PyTorch, puis aux modèles audio, à la génération, à l’évaluation et à l’oral. Ces semaines sont des repères à adapter, sans dates imposées.</p><details class="quick-survey"><summary>Les chapitres Python et Signal à survoler si les bases sont acquises</summary><p>Connaître le mel ne garantit pas de maîtriser les axes, les niveaux ou la phase. Nous gardons les chapitres utiles dès qu’un doute apparaît.</p><ul>${QUICK_CHAPTERS.map(chapter=>`<li><a href="${courseHref(chapter.themeId,chapter.chapterId)}">${esc(find(chapter.themeId,chapter.chapterId).title)}</a><p>${esc(chapter.condition)}</p></li>`).join('')}</ul></details><div class="revision-weeks">${REVISION_WEEKS.map(week=>`<section><h3>${esc(week.title)}</h3><p>${esc(week.goal)}</p><ol>${week.links.map(link=>`<li><a href="${courseHref(link.themeId,link.chapterId)}">${esc(link.text)}</a></li>`).join('')}</ol><p class="revision-deliverable"><strong>Pour vérifier.</strong> ${esc(week.deliverable)}</p></section>`).join('')}</div></details>`;
}

function renderModuleIntroduction(course) {
  const introduction=course.moduleIntroduction;
  if(!introduction)return '';
  return `<section class="module-introduction"><p><strong>Pour commencer.</strong> ${esc(introduction.startingPoint)}</p><p class="module-goal"><strong>À la fin de ce module.</strong> ${esc(introduction.goal)}</p><h3>Les notions que nous allons découvrir, dans l’ordre</h3><ol>${introduction.concepts.map(concept=>`<li><a href="${courseHref(course.themeId,concept.chapterId)}">${esc(concept.name)}</a><p>${esc(concept.explanation)}</p></li>`).join('')}</ol><button type="button" class="module-begin">Aller au chapitre ↓</button></section>`;
}

function renderNotions(chapter) {
  if(!chapter.notions?.length)return '';
  return `<details class="introduced-notions"><summary><strong>Les notions de ce chapitre</strong><span>${chapter.notions.map(notion=>esc(notion.name)).join(' · ')}</span></summary><ul>${chapter.notions.map(notion=>`<li><strong>${esc(notion.name)}</strong><p>${esc(notion.explanation)}</p></li>`).join('')}</ul></details>`;
}

function renderJourney(course,chapter) {
  if(!course.journey)return '';
  const journey=course.journey,current=courseStage(course,chapter.id);
  return `<details class="course-journey" ${chapter===course.chapters[0]?'open':''}><summary><span><small>PRÉSENTATION DU MODULE</small><strong>${esc(name(course.themeId))}</strong></span><span class="journey-toggle" aria-hidden="true">+</span></summary><div class="journey-content">${renderModuleIntroduction(course)}<details class="module-project"><summary>Le projet et les étapes du module</summary><h3>${esc(journey.title)}</h3><p class="journey-scenario">${esc(journey.scenario)}</p><div class="journey-endpoints"><div><span>Au départ</span><p>${esc(journey.startingPoint)}</p></div><div><span>À l’arrivée</span><p>${esc(journey.destination)}</p></div></div><ol class="journey-stages">${journey.stages.map((stage,index)=>`<li class="${stage===current?'is-current':''}"><a href="${courseHref(course.themeId,stage.chapterIds[0])}" ${stage===current?'aria-current="step"':''}><span>${String(index+1).padStart(2,'0')}</span><strong>${esc(stage.title)}</strong><small>${stage.chapterIds.length} chapitre${stage.chapterIds.length===1?'':'s'}${stage===current?' · Vous êtes ici':''}</small></a></li>`).join('')}</ol><details class="interview-scope"><summary>Ce que ce cours vous aide à expliquer en entretien</summary><ul>${journey.scope.map(item=>`<li>${esc(item)}</li>`).join('')}</ul></details></details></div></details>`;
}

function renderNotebook(chapter) {
  if(!chapter.notebook)return '';
  const links=notebookLinks(chapter.notebook,import.meta.env.BASE_URL);
  return `<details class="chapter-notebook"><summary>Pratiquer ce chapitre dans un notebook</summary><p>Les démonstrations et les deux exercices sont séparés. Les cellules d’exercice sont prêtes à modifier ; les indices précèdent les solutions.</p><div><a class="button primary" href="${esc(links.colab)}" target="_blank" rel="noopener noreferrer">Ouvrir dans Colab ↗</a><a class="button secondary" href="${esc(links.download)}" download>Télécharger le notebook</a></div><p class="notebook-environment">Environnement vérifié : Python 3.11 et PyTorch 2.10, sur CPU. La préparation est détaillée dans le notebook.</p></details>`;
}

function renderContext(chapter,course) {
  if(!chapter.context)return '';
  const stage=courseStage(course,chapter.id),step=chapter.progression??{input:chapter.context.recall,action:chapter.context.problem,output:chapter.context.why};
  return `<section class="chapter-context" aria-label="Repères du chapitre">${renderNotions(chapter)}<details class="chapter-position"><summary>Situer cette étape dans le parcours</summary><p class="eyebrow">${stage?esc(stage.title):'LE FIL DU PARCOURS'}</p><dl class="chapter-progression"><div><dt>Nous partons de</dt><dd>${esc(step.input)}</dd></div><div><dt>Nous allons</dt><dd>${esc(step.action)}</dd></div><div><dt>Nous obtenons</dt><dd>${esc(step.output)}</dd></div></dl></details></section>`;
}

function renderLevel(chapter){
  const names={practice:'Socle à pratiquer',discuss:'À discuter',advanced:'Approfondissement'};
  const prereqs=chapter.prerequisites??[];
  return `${chapter.level?`<p class="lesson-level">${esc(names[chapter.level]??chapter.level)}</p>`:''}${prereqs.length?`<div class="chapter-prerequisites"><span>À comprendre avant :</span> ${prereqs.map(link=>`<a href="${courseHref(link.themeId,link.chapterId)}">${esc(link.text??link.chapterId)}</a>`).join(' · ')}</div>`:''}`;
}

function renderMethodology() {
  if(!pedagogy)return '';
  return `<details class="learning-methodology"><summary>Pourquoi les cours sont construits ainsi <span>Sources et méthode pédagogique</span></summary><h2>${esc(pedagogy.title)}</h2><p>${esc(pedagogy.intro)}</p><div class="method-principles">${pedagogy.principles.map(principle=>`<section><h3>${esc(principle.title)}</h3><p>${esc(principle.text)}</p></section>`).join('')}</div><p>${esc(pedagogy.limits)}</p><ul>${pedagogy.sources.map(source=>`<li><a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">${esc(source.title)} ↗</a><p>${esc(source.role)}</p></li>`).join('')}</ul></details>`;
}

function showOverview() {
  activeReadKey=null;
  document.title = 'Les cours de Squoinks — À l’écoute';
  document.body.classList.remove('reading-focus','large-reading-text');
  const allChapters = courses.reduce((total,c)=>total+c.chapters.length,0);
  const last = progress.last && courses.find(c=>c.themeId===progress.last.themeId);
  const lastChapter = last?.chapters.find(ch=>ch.id===progress.last.chapterId);
  root.innerHTML = `<section class="courses-hero"><div><p class="eyebrow"><span class="small-dot"></span> L’ATELIER DU PROFESSEUR SQUOINKS</p><h1>Les idées prennent<br><span>le temps de faire tilt.</span></h1><p class="courses-lead">Avant de trouver la bonne réponse, comprenons ce qui se passe. Des cours illustrés pour passer du Python algorithmique à la préparation audio, aux modèles et à leur évaluation.</p><div class="course-facts"><span><strong>${courses.length}</strong> modules</span><span><strong>${allChapters}</strong> chapitres</span><span><strong>200</strong> questions éclairées</span></div></div><figure class="professor-hero"><img src="${portrait}" width="360" height="360" alt="Le professeur Squoinks, scientifique souriant aux cheveux bleus et à la moustache bleue, tient un carnet illustré d’une onde sonore."><figcaption>Professeur Squoinks<br><span>« Une idée à la fois. Le reste attendra. »</span></figcaption></figure></section>${storageNotice()}${lastChapter?`<aside class="reading-resume"><div><p class="eyebrow">ON REPREND LE FIL ?</p><strong>${esc(lastChapter.title)}</strong><p>${esc(name(last.themeId))}</p></div><a class="button primary" href="${courseHref(last.themeId,lastChapter.id)}">Reprendre la lecture <span aria-hidden="true">→</span></a></aside>`:''}<section class="course-path" aria-labelledby="path-title"><div class="course-path-heading"><div><p class="eyebrow">LE PARCOURS / DU CONCRET AU COMPLEXE</p><h2 id="path-title">Un fil à suivre, plusieurs portes à ouvrir.</h2></div><p>Suivez l’ordre proposé ou entrez par le thème qui vous intéresse.</p></div><div class="course-cards">${courses.map((course,i)=>{
    const read=readCount(course);
    return `<a class="course-card" href="${courseHref(course.themeId)}"><div class="course-card-top"><span class="course-index">${String(i+1).padStart(2,'0')}</span><span>${course.chapters.length} chapitres · ≈ ${minutes(course)} min de lecture</span></div><h3>${esc(name(course.themeId))}</h3><p>${esc(course.subtitle)}</p><div class="course-card-footer"><span>${read?`${read} / ${course.chapters.length} lus`:'Ouvrir le cours'}</span><span aria-hidden="true">↗</span></div><progress max="${course.chapters.length}" value="${read}" aria-label="${esc(name(course.themeId))} : ${read} chapitres lus"></progress></a>`;
  }).join('')}</div></section><section class="reading-method"><div><p class="eyebrow">FAITES SIMPLE</p><h2>Pas besoin de tout lire d’un coup.</h2></div><ol><li><strong>Une petite étape.</strong><span>Un chapitre, une idée directrice, quelques minutes de lecture.</span></li><li><strong>Le droit de faire une pause.</strong><span>Marquez ce que vous avez lu. Retrouvez votre dernier chapitre ici.</span></li><li><strong>Du sens avant la mémoire.</strong><span>Exemples, schémas et pièges classiques pour comprendre les réponses du quiz.</span></li></ol><p class="course-honesty">Les durées sont indicatives. « Lu » est un repère personnel, pas une validation de maîtrise. Aucun chronomètre, aucune obligation de terminer.</p></section>`;
  root.querySelector('.courses-hero').insertAdjacentHTML('afterend',renderGlobalRoadmap());
  root.querySelector('.global-learning-goal').insertAdjacentHTML('afterend',renderRevisionPath());
  root.insertAdjacentHTML('beforeend',renderMethodology());
}

function showCourse(course, chapter) {
  const index = course.chapters.indexOf(chapter);
  const key=readKey(course,chapter);
  const chapterState=progress.chapterStates[key]??={walkthroughs:{},scrollY:0};
  activeReadKey=key;
  if(chapter.checkpoint&&chapterState.checkpointSignature!==checkpointSignature(chapter.checkpoint)){
    delete chapterState.chosenId;delete chapterState.optionOrder;
    chapterState.checkpointSignature=checkpointSignature(chapter.checkpoint);
  }
  const {previous:previousChapter,next:nextChapter}=chapterNavigation(course,chapter);
  const isRead = progress.completed.includes(readKey(course,chapter));
  const count = readCount(course);
  const query = new URLSearchParams(location.search).get('question');
  const fromQuestion = query && chapter.questionIds.includes(query) && bank.find(q=>q.id===query);
  progress.last = {themeId:course.themeId,chapterId:chapter.id};
  save(); applyPreferences();
  document.title = `${chapter.title} — ${name(course.themeId)} — À l’écoute`;
  root.innerHTML = `<div class="course-breadcrumb"><a href="./cours.html">Tous les cours</a><span aria-hidden="true">/</span><span>${esc(name(course.themeId))}</span></div>${renderJourney(course,chapter)}<div class="course-layout"><aside class="course-sidebar"><div class="sidebar-title"><span class="eyebrow">LE FIL DU COURS</span><h2>${esc(name(course.themeId))}</h2><p>${count} / ${course.chapters.length} chapitres lus</p><progress max="${course.chapters.length}" value="${count}" aria-label="Progression de lecture"></progress></div><details class="chapter-toc" open><summary>Sommaire <span>${index+1} / ${course.chapters.length}</span></summary><nav aria-label="Chapitres du cours"><ol>${course.chapters.map((ch,i)=>`<li><a href="${courseHref(course.themeId,ch.id)}" ${ch.id===chapter.id?'aria-current="step"':''}><span class="toc-number">${progress.completed.includes(readKey(course,ch))?'✓':String(i+1).padStart(2,'0')}</span><span>${esc(ch.title)}${quickBadge(course.themeId,ch.id)}${ch.readingRole==='reference'?'<small class="reference-label">Complément facultatif</small>':''}${progress.completed.includes(readKey(course,ch))?'<span class="sr-only"> — lu</span>':''}</span></a></li>`).join('')}</ol></nav></details><details class="course-introduction"><summary>Avant de commencer</summary>${course.intro.map(p=>`<p>${esc(p)}</p>`).join('')}<h3>Ce que vous allez comprendre</h3><ul>${course.objectives.map(p=>`<li>${esc(p)}</li>`).join('')}</ul>${course.prerequisites.length?`<h3>Des bases utiles avant ce cours</h3>${course.prerequisites.map(id=>`<a class="prerequisite" href="${courseHref(id)}">${esc(name(id))} ↗</a>`).join('')}`:'<p>Les bases du Python algorithmique sont supposées connues. Les notions scientifiques sont expliquées au fil du projet.</p>'}</details></aside><article class="lesson" aria-labelledby="lesson-title"><div class="lesson-tools"><span class="eyebrow">${chapter.readingRole==='reference'?'COMPLÉMENT':'CHAPITRE'} ${String(index+1).padStart(2,'0')} / ${String(course.chapters.length).padStart(2,'0')}</span><div><button id="large-text" aria-pressed="${progress.largeText}" aria-label="Agrandir le texte du cours">Aa +</button><button id="reading-mode" aria-pressed="${progress.readingMode}">${progress.readingMode?'Afficher le sommaire':'Mode lecture'}</button></div></div><header class="lesson-heading"><span class="lesson-time">≈ ${chapterMinutes(chapter)} min de lecture · pratique à votre rythme</span><h1 id="lesson-title">${esc(chapter.title)}</h1><p class="lesson-summary">${esc(chapter.summary)}</p>${renderLevel(chapter)}</header>${renderQuickNote(course,chapter)}${renderContext(chapter,course)}${storageNotice()}${fromQuestion?`<aside class="question-context"><span>↳ Depuis le quiz</span><p>${esc(fromQuestion.prompt)}</p><small>Voici le chapitre qui explique la notion. Votre session reste sauvegardée.</small></aside>`:''}<div class="lesson-body">${renderLessonBody(chapter)}</div>${chapter.oral?'':`<details class="takeaway"><summary>Relire les repères du chapitre</summary><ol>${chapter.takeaways.map(t=>`<li>${esc(t)}</li>`).join('')}</ol></details>`}${chapter.checkpoint?renderCheckpoint(chapter.checkpoint,chapterState.optionOrder):''}<div class="chapter-completion"><label><input type="checkbox" id="mark-read" ${isRead?'checked':''}><span><strong>J’ai lu ce chapitre</strong><small>Un repère pour vous, sans test ni obligation.</small></span></label><label class="review-control"><input type="checkbox" id="mark-review" ${progress.review.includes(readKey(course,chapter))?'checked':''}><span>À revoir</span></label><span class="read-status" role="status">${isRead?'Repère enregistré':'À votre rythme'}</span></div>${references(chapter.sourceIds)}${chapter.context?`<aside class="next-connection"><strong>Et maintenant ?</strong><p>${esc(chapter.context.next)}</p></aside>`:''}<nav class="chapter-pagination" aria-label="Continuer la lecture">${previousChapter?`<a class="chapter-prev" href="${courseHref(course.themeId,previousChapter.id)}"><span>← Chapitre précédent</span><strong>${esc(previousChapter.title)}</strong></a>`:'<a class="chapter-prev" href="./cours.html"><span>← Tous les cours</span><strong>Retrouver le parcours</strong></a>'}${nextChapter?`<a class="chapter-next" href="${courseHref(course.themeId,nextChapter.id)}"><span>Chapitre suivant →</span><strong>${esc(nextChapter.title)}</strong></a>`:nextCourse(course)}</nav><div class="lesson-quiz-link"><img src="${portrait}" alt="" width="68" height="68" loading="lazy"><p>Les notions ont pris forme ?<br><span>Le quiz est là pour les remettre en mouvement.</span></p><a class="button secondary" href="./">Retour au quiz ↗</a></div></article></div>`;
  const pitchFields=[...root.querySelectorAll('[data-pitch-field]')];
  if(pitchFields.length){
    const draft=storage.read('a-lecoute.pitch.v1');
    pitchFields.forEach((field,index)=>{field.value=typeof draft?.[index]==='string'?draft[index].slice(0,5000):'';});
    pitchFields.forEach(field=>field.addEventListener('input',()=>{
      storage.write('a-lecoute.pitch.v1',pitchFields.map(input=>input.value));
      root.querySelector('.pitch-save-status').textContent=storage.available?'Notes enregistrées sur cet appareil.':'Stockage indisponible : copiez vos notes avant de quitter la page.';
    }));
  }
  root.querySelector('.module-begin')?.addEventListener('click',()=>{
    const heading=root.querySelector('#lesson-title');heading.tabIndex=-1;heading.focus({preventScroll:true});
    root.querySelector('.lesson').scrollIntoView({block:'start',behavior:'instant'});
  });
  root.querySelectorAll('.copy-course-code').forEach(button=>button.addEventListener('click',async()=>{
    const code=button.closest('.lesson-code').querySelector('code').textContent;
    try{await navigator.clipboard.writeText(code);button.textContent='Code copié';}
    catch{button.textContent='Sélectionnez le code pour le copier';}
  }));
  attachWalkthroughs(root,chapter.blocks,{state:chapterState.walkthroughs,onChange:()=>save()});
  attachTensorLabs(root,chapter.blocks);
  attachAudioLabs(root,chapter.blocks,audioMedia,import.meta.env.BASE_URL);
  if(chapter.checkpoint){
    chapterState.optionOrder=[...root.querySelectorAll('[data-checkpoint-option]')].map(option=>option.dataset.checkpointOption);
    attachCheckpoint(root,chapter.checkpoint,{chosenId:chapterState.chosenId,onChange:id=>{chapterState.chosenId=id;save();}});
  }
  if(window.matchMedia('(max-width:740px)').matches) root.querySelector('.chapter-toc').open=false;
  root.querySelector('#mark-read').addEventListener('change',event=>{
    progress=setChapterRead(progress,course.themeId,chapter.id,event.target.checked);
    save();
    // Update the small progress indicators without replacing the article or its scroll position.
    const currentCount=readCount(course);
    root.querySelector('.sidebar-title p').textContent=`${currentCount} / ${course.chapters.length} chapitres lus`;
    root.querySelector('.sidebar-title progress').value=currentCount;
    root.querySelector('.read-status').textContent=storage.available?(event.target.checked?'Repère enregistré':'Chapitre remis à lire'):'Repère conservé en mémoire seulement';
    const currentLink=root.querySelector('.chapter-toc [aria-current="step"]');
    currentLink.querySelector('.toc-number').textContent=event.target.checked?'✓':String(index+1).padStart(2,'0');
    currentLink.setAttribute('aria-label',`${chapter.title}${event.target.checked?' — lu':''}`);
  });
  root.querySelector('#mark-review').addEventListener('change',event=>{
    progress=setChapterReview(progress,course.themeId,chapter.id,event.target.checked);save();
  });
  root.querySelector('#large-text').addEventListener('click',event=>{
    preserveReadingPosition(()=>{progress.largeText=!progress.largeText;save();applyPreferences();event.currentTarget.setAttribute('aria-pressed',progress.largeText);});
  });
  root.querySelector('#reading-mode').addEventListener('click',event=>{
    preserveReadingPosition(()=>{progress.readingMode=!progress.readingMode;save();applyPreferences();event.currentTarget.setAttribute('aria-pressed',progress.readingMode);event.currentTarget.textContent=progress.readingMode?'Afficher le sommaire':'Mode lecture';});
  });
}

function nextCourse(course) {
  const next=courses[courses.indexOf(course)+1];
  return next?`<a class="chapter-next" href="${courseHref(next.themeId)}"><span>Explorer le thème suivant →</span><strong>${esc(name(next.themeId))}</strong></a>`:'<a class="chapter-next" href="./"><span>Passer à la pratique →</span><strong>Retrouver le quiz</strong></a>';
}

function route({ focus=false,restore=false } = {}) {
  rememberReading();
  root.querySelectorAll('audio').forEach(audio=>audio.pause());
  const params=new URLSearchParams(location.search);
  const course=courses.find(c=>c.themeId===params.get('theme'));
  if(course) {
    let chapterId;
    try { chapterId=decodeURIComponent(location.hash.slice(1)); } catch { chapterId=''; }
    showCourse(course,resolveChapter(course,{chapterId,questionId:params.get('question')}));
  } else showOverview();
  if(restore&&activeReadKey){
    const y=progress.chapterStates[activeReadKey]?.scrollY??0;
    requestAnimationFrame(()=>window.scrollTo({top:y,behavior:'instant'}));
  }else if(focus) focusReading();
}

async function init() {
  try {
    ({themes,sources,bank}=await loadBank());
    courses=await Promise.all(COURSE_ORDER.map(async id=>{
      const response=await fetch(`${import.meta.env.BASE_URL}courses/${id}.json`,{cache:'no-cache'});
      if(!response.ok)throw new Error(`Cours indisponible : ${id}`);
      return response.json();
    }));
    sources=mergeCourseReferences(sources,courses);
    const methodResponse=await fetch(`${import.meta.env.BASE_URL}courses/pedagogy.json`,{cache:'no-cache'});
    if(!methodResponse.ok)throw new Error('Méthode pédagogique indisponible');
    pedagogy=await methodResponse.json();
    [audioMedia,illustrations]=await Promise.all(['audio-lab','illustrations'].map(async file=>{
      const response=await fetch(`${import.meta.env.BASE_URL}media/${file}.json`,{cache:'no-cache'});
      if(!response.ok)throw new Error('Médias du cours indisponibles');
      return response.json();
    }));
    root.addEventListener('play',event=>{
      if(event.target.tagName==='AUDIO')root.querySelectorAll('audio').forEach(audio=>{if(audio!==event.target)audio.pause();});
    },true);
    coverage=buildCoverage(courses);
    if(bank.some(q=>!coverage.has(q.id))) throw new Error('Les cours ne couvrent pas toute la banque.');
    progress=normalizeProgress(storage.read(COURSE_STORAGE_KEY),courses);
    route({restore:true});
    window.addEventListener('scroll',()=>{clearTimeout(scrollWriteTimer);scrollWriteTimer=setTimeout(rememberReading,180);},{passive:true});
    document.addEventListener('click',event=>{
      const anchor=event.target.closest('a[href]');
      if(!anchor||event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||anchor.target||anchor.hasAttribute('download'))return;
      if(anchor.getAttribute('href')==='#app'){event.preventDefault();root.focus();return;}
      const target=new URL(anchor.href,location.href);
      if(target.origin!==location.origin||target.pathname!==location.pathname)return;
      if(!anchor.getAttribute('href').includes('cours.html'))return;
      event.preventDefault();history.pushState(null,'',target);route({focus:true});
    });
    window.addEventListener('popstate',()=>route({restore:true}));
    window.addEventListener('hashchange',()=>route({focus:true}));
  } catch(error) {
    console.error(error);
    root.innerHTML='<section class="load-error"><h1>Les cours n’ont pas pu être chargés.</h1><p>Vérifiez que le serveur local est lancé et que les fichiers des cours sont présents.</p><button class="button primary" id="retry-courses">Réessayer</button><a class="button secondary" href="./">Retour au quiz</a></section>';
    root.querySelector('#retry-courses').addEventListener('click',()=>location.reload());
  }
}
init();
