import './style.css';
import './courses.css';
import { loadBank } from './bank.js';
import { createStorage } from './storage.js';
import { COURSE_ORDER, COURSE_STORAGE_KEY, courseHref, buildCoverage, chapterMinutes, normalizeProgress, setChapterRead, resolveChapter } from './course-model.js';
import { renderFigure } from './course-figures.js';

const root = document.querySelector('#app');
const storage = createStorage();
const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' })[c]);
const portrait = `${import.meta.env.BASE_URL}images/professeur-squoinks.png`;
let courses = [], themes = [], sources = [], bank = [], progress, coverage;
let serial = 0;
const name = id => themes.find(t => t.id === id)?.label ?? id;
const readKey = (course, chapter) => `${course.themeId}/${chapter.id}`;
const minutes = course => course.chapters.reduce((sum, ch) => sum + chapterMinutes(ch), 0);
const readCount = course => course.chapters.filter(ch => progress.completed.includes(readKey(course,ch))).length;
function save() { storage.write(COURSE_STORAGE_KEY, progress); }
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
  if(block.type==='paragraph') return `<p>${esc(block.text)}</p>`;
  if(block.type==='heading') return `<h3>${esc(block.text)}</h3>`;
  if(block.type==='list') return `<div class="lesson-list">${block.title?`<h3>${esc(block.title)}</h3>`:''}<ul>${block.items.map(item=>`<li>${esc(item)}</li>`).join('')}</ul></div>`;
  if(block.type==='code') return `<figure class="lesson-code"><div class="code-label">${esc(block.language ?? 'python')} · EXEMPLE COMMENTÉ</div><pre><code>${esc(block.code)}</code></pre>${block.caption?`<figcaption>${esc(block.caption)}</figcaption>`:''}</figure>`;
  if(block.type==='callout') return `<aside class="lesson-callout ${esc(block.tone)}"><span class="callout-symbol" aria-hidden="true">${block.tone==='analogy'?'↔':block.tone==='pitfall'?'!':'↳'}</span><div><h3>${esc(block.label)}</h3><p>${esc(block.text)}</p></div></aside>`;
  if(block.type==='example') return `<section class="real-example"><p class="eyebrow">DANS LA VRAIE VIE</p><h3>${esc(block.title)}</h3><p>${esc(block.text)}</p></section>`;
  if(block.type==='figure') return renderFigure(block.kind,block.caption,++serial);
  return '';
}

function showOverview() {
  document.title = 'Les cours de Squoinks — À l’écoute';
  document.body.classList.remove('reading-focus','large-reading-text');
  const allChapters = courses.reduce((total,c)=>total+c.chapters.length,0);
  const last = progress.last && courses.find(c=>c.themeId===progress.last.themeId);
  const lastChapter = last?.chapters.find(ch=>ch.id===progress.last.chapterId);
  root.innerHTML = `<section class="courses-hero"><div><p class="eyebrow"><span class="small-dot"></span> L’ATELIER DU PROFESSEUR SQUOINKS</p><h1>Les idées prennent<br><span>le temps de faire tilt.</span></h1><p class="courses-lead">Avant de trouver la bonne réponse, comprenons ce qui se passe. Six cours illustrés, du premier tableau Python aux modèles qui fabriquent du son.</p><div class="course-facts"><span><strong>6</strong> thèmes</span><span><strong>${allChapters}</strong> chapitres courts</span><span><strong>200</strong> questions éclairées</span></div></div><figure class="professor-hero"><img src="${portrait}" width="360" height="360" alt="Le professeur Squoinks, scientifique souriant aux cheveux bleus et à la moustache bleue, tient un carnet illustré d’une onde sonore."><figcaption>Professeur Squoinks<br><span>« Une idée à la fois. Le reste attendra. »</span></figcaption></figure></section>${storageNotice()}${lastChapter?`<aside class="reading-resume"><div><p class="eyebrow">ON REPREND LE FIL ?</p><strong>${esc(lastChapter.title)}</strong><p>${esc(name(last.themeId))}</p></div><a class="button primary" href="${courseHref(last.themeId,lastChapter.id)}">Reprendre la lecture <span aria-hidden="true">→</span></a></aside>`:''}<section class="course-path" aria-labelledby="path-title"><div class="course-path-heading"><div><p class="eyebrow">LE PARCOURS / DU CONCRET AU COMPLEXE</p><h2 id="path-title">Un fil à suivre. Six portes à ouvrir.</h2></div><p>Suivez l’ordre proposé ou entrez par le thème qui vous intéresse.</p></div><div class="course-cards">${courses.map((course,i)=>{
    const read=readCount(course);
    return `<a class="course-card" href="${courseHref(course.themeId)}"><div class="course-card-top"><span class="course-index">${String(i+1).padStart(2,'0')}</span><span>${course.chapters.length} chapitres · ≈ ${minutes(course)} min</span></div><h3>${esc(name(course.themeId))}</h3><p>${esc(course.subtitle)}</p><div class="course-card-footer"><span>${read?`${read} / ${course.chapters.length} lus`:'Ouvrir le cours'}</span><span aria-hidden="true">↗</span></div><progress max="${course.chapters.length}" value="${read}" aria-label="${esc(name(course.themeId))} : ${read} chapitres lus"></progress></a>`;
  }).join('')}</div></section><section class="reading-method"><div><p class="eyebrow">FAITES SIMPLE</p><h2>Pas besoin de tout lire d’un coup.</h2></div><ol><li><strong>Une petite étape.</strong><span>Un chapitre, une idée directrice, quelques minutes de lecture.</span></li><li><strong>Le droit de faire une pause.</strong><span>Marquez ce que vous avez lu. Retrouvez votre dernier chapitre ici.</span></li><li><strong>Du sens avant la mémoire.</strong><span>Exemples, schémas et pièges classiques pour comprendre les réponses du quiz.</span></li></ol><p class="course-honesty">Les durées sont indicatives. « Lu » est un repère personnel, pas une validation de maîtrise. Aucun chronomètre, aucune obligation de terminer.</p></section>`;
}

function showCourse(course, chapter) {
  const index = course.chapters.indexOf(chapter);
  const isRead = progress.completed.includes(readKey(course,chapter));
  const count = readCount(course);
  const query = new URLSearchParams(location.search).get('question');
  const fromQuestion = query && chapter.questionIds.includes(query) && bank.find(q=>q.id===query);
  progress.last = {themeId:course.themeId,chapterId:chapter.id};
  save(); applyPreferences();
  document.title = `${chapter.title} — ${name(course.themeId)} — À l’écoute`;
  root.innerHTML = `<div class="course-breadcrumb"><a href="./cours.html">Tous les cours</a><span aria-hidden="true">/</span><span>${esc(name(course.themeId))}</span></div><div class="course-layout"><aside class="course-sidebar"><div class="sidebar-title"><span class="eyebrow">LE FIL DU COURS</span><h2>${esc(name(course.themeId))}</h2><p>${count} / ${course.chapters.length} chapitres lus</p><progress max="${course.chapters.length}" value="${count}" aria-label="Progression de lecture"></progress></div><details class="chapter-toc" open><summary>Sommaire <span>${index+1} / ${course.chapters.length}</span></summary><nav aria-label="Chapitres du cours"><ol>${course.chapters.map((ch,i)=>`<li><a href="${courseHref(course.themeId,ch.id)}" ${ch.id===chapter.id?'aria-current="step"':''}><span class="toc-number">${progress.completed.includes(readKey(course,ch))?'✓':String(i+1).padStart(2,'0')}</span><span>${esc(ch.title)}${progress.completed.includes(readKey(course,ch))?'<span class="sr-only"> — lu</span>':''}</span></a></li>`).join('')}</ol></nav></details><details class="course-introduction"><summary>Avant de commencer</summary>${course.intro.map(p=>`<p>${esc(p)}</p>`).join('')}<h3>Ce que vous allez comprendre</h3><ul>${course.objectives.map(p=>`<li>${esc(p)}</li>`).join('')}</ul>${course.prerequisites.length?`<h3>Des bases utiles avant ce cours</h3>${course.prerequisites.map(id=>`<a class="prerequisite" href="${courseHref(id)}">${esc(name(id))} ↗</a>`).join('')}`:'<p>Vous pouvez commencer ici sans autre cours du parcours.</p>'}</details></aside><article class="lesson" aria-labelledby="lesson-title"><div class="lesson-tools"><span class="eyebrow">CHAPITRE ${String(index+1).padStart(2,'0')} / ${String(course.chapters.length).padStart(2,'0')}</span><div><button id="large-text" aria-pressed="${progress.largeText}" aria-label="Agrandir le texte du cours">Aa +</button><button id="reading-mode" aria-pressed="${progress.readingMode}">${progress.readingMode?'Afficher le sommaire':'Mode lecture'}</button></div></div><header class="lesson-heading"><span class="lesson-time">≈ ${chapterMinutes(chapter)} min · À votre rythme</span><h1 id="lesson-title">${esc(chapter.title)}</h1><p class="lesson-summary">${esc(chapter.summary)}</p></header>${storageNotice()}${fromQuestion?`<aside class="question-context"><span>↳ Depuis le quiz</span><p>${esc(fromQuestion.prompt)}</p><small>Voici le chapitre qui explique la notion. Votre session reste sauvegardée.</small></aside>`:''}<div class="lesson-body">${chapter.blocks.map(renderBlock).join('')}</div><section class="takeaway"><p class="eyebrow">SI VOUS NE GARDEZ QUE TROIS IDÉES</p><h2>L’essentiel, sans les détours.</h2><ol>${chapter.takeaways.map(t=>`<li>${esc(t)}</li>`).join('')}</ol></section><div class="chapter-completion"><label><input type="checkbox" id="mark-read" ${isRead?'checked':''}><span><strong>J’ai lu ce chapitre</strong><small>Un repère pour vous, sans test ni obligation.</small></span></label><span class="read-status" role="status">${isRead?'Repère enregistré':'À votre rythme'}</span></div>${references(chapter.sourceIds)}<nav class="chapter-pagination" aria-label="Continuer la lecture">${index?`<a class="chapter-prev" href="${courseHref(course.themeId,course.chapters[index-1].id)}"><span>← Chapitre précédent</span><strong>${esc(course.chapters[index-1].title)}</strong></a>`:'<a class="chapter-prev" href="./cours.html"><span>← Tous les cours</span><strong>Retrouver le parcours</strong></a>'}${index<course.chapters.length-1?`<a class="chapter-next" href="${courseHref(course.themeId,course.chapters[index+1].id)}"><span>Chapitre suivant →</span><strong>${esc(course.chapters[index+1].title)}</strong></a>`:nextCourse(course)}</nav><div class="lesson-quiz-link"><img src="${portrait}" alt="" width="68" height="68" loading="lazy"><p>Les notions ont pris forme ?<br><span>Le quiz est là pour les remettre en mouvement.</span></p><a class="button secondary" href="./">Retour au quiz ↗</a></div></article></div>`;
  if(window.matchMedia('(max-width:740px)').matches) root.querySelector('.chapter-toc').open=false;
  root.querySelector('#mark-read').addEventListener('change',event=>{
    progress=setChapterRead(progress,course.themeId,chapter.id,event.target.checked);
    save();
    // Update the small progress indicators without replacing the article or its scroll position.
    const currentCount=readCount(course);
    root.querySelector('.sidebar-title p').textContent=`${currentCount} / ${course.chapters.length} chapitres lus`;
    root.querySelector('.sidebar-title progress').value=currentCount;
    root.querySelector('.read-status').textContent=storage.available?(event.target.checked?'Repère enregistré':'Chapitre remis à lire'):'Repère conservé en mémoire seulement';
    const currentLink=root.querySelector('[aria-current="step"]');
    currentLink.querySelector('.toc-number').textContent=event.target.checked?'✓':String(index+1).padStart(2,'0');
    currentLink.setAttribute('aria-label',`${chapter.title}${event.target.checked?' — lu':''}`);
  });
  root.querySelector('#large-text').addEventListener('click',event=>{
    progress.largeText=!progress.largeText;save();applyPreferences();event.currentTarget.setAttribute('aria-pressed',progress.largeText);
  });
  root.querySelector('#reading-mode').addEventListener('click',event=>{
    progress.readingMode=!progress.readingMode;save();applyPreferences();event.currentTarget.setAttribute('aria-pressed',progress.readingMode);event.currentTarget.textContent=progress.readingMode?'Afficher le sommaire':'Mode lecture';
  });
}

function nextCourse(course) {
  const next=courses[courses.indexOf(course)+1];
  return next?`<a class="chapter-next" href="${courseHref(next.themeId)}"><span>Explorer le thème suivant →</span><strong>${esc(name(next.themeId))}</strong></a>`:'<a class="chapter-next" href="./"><span>Passer à la pratique →</span><strong>Retrouver le quiz</strong></a>';
}

function route({ focus=false } = {}) {
  const params=new URLSearchParams(location.search);
  const course=courses.find(c=>c.themeId===params.get('theme'));
  if(course) {
    let chapterId;
    try { chapterId=decodeURIComponent(location.hash.slice(1)); } catch { chapterId=''; }
    showCourse(course,resolveChapter(course,{chapterId,questionId:params.get('question')}));
  } else showOverview();
  if(focus) focusReading();
}

async function init() {
  try {
    ({themes,sources,bank}=await loadBank());
    courses=await Promise.all(COURSE_ORDER.map(async id=>{
      const response=await fetch(`${import.meta.env.BASE_URL}courses/${id}.json`);
      if(!response.ok)throw new Error(`Cours indisponible : ${id}`);
      return response.json();
    }));
    coverage=buildCoverage(courses);
    if(bank.some(q=>!coverage.has(q.id))) throw new Error('Les cours ne couvrent pas toute la banque.');
    progress=normalizeProgress(storage.read(COURSE_STORAGE_KEY),courses);
    route();
    document.addEventListener('click',event=>{
      const anchor=event.target.closest('a[href]');
      if(!anchor||event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||anchor.target||anchor.hasAttribute('download'))return;
      const target=new URL(anchor.href,location.href);
      if(target.origin!==location.origin||target.pathname!==location.pathname)return;
      if(!anchor.getAttribute('href').includes('cours.html'))return;
      event.preventDefault();history.pushState(null,'',target);route({focus:true});
    });
    window.addEventListener('popstate',()=>route({focus:true}));
    window.addEventListener('hashchange',()=>route({focus:true}));
  } catch(error) {
    console.error(error);
    root.innerHTML='<section class="load-error"><h1>Les cours n’ont pas pu être chargés.</h1><p>Vérifiez que le serveur local est lancé et que les fichiers des cours sont présents.</p><button class="button primary" id="retry-courses">Réessayer</button><a class="button secondary" href="./">Retour au quiz</a></section>';
    root.querySelector('#retry-courses').addEventListener('click',()=>location.reload());
  }
}
init();
