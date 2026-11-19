import {courseHref,readingProgress,chapterPosition} from './course-model.js';
const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[char]);

export function readingPositionLabel(course,chapter){
  const place=chapterPosition(course,chapter);
  if(course.readingGroups)return place.reference?`FICHE ${String.fromCharCode(64+place.position)} · À LA DEMANDE`:`CHAPITRE ${place.position} / ${place.total}`;
  return `${place.reference?'COMPLÉMENT':'CHAPITRE'} ${String(place.position).padStart(2,'0')} / ${String(place.total).padStart(2,'0')}`;
}

export function renderNarrativeSidebar(course,chapter,progress){
  const counts=readingProgress(course,progress),references=course.chapters.filter(item=>item.readingRole==='reference');
  const read=item=>progress.completed.includes(`${course.themeId}/${item.id}`);
  const chapterLink=item=>{
    const place=chapterPosition(course,item),number=place.reference?String.fromCharCode(64+place.position):String(place.position).padStart(2,'0');
    return `<li><a href="${courseHref(course.themeId,item.id)}" ${item.id===chapter.id?'aria-current="step"':''}><span class="toc-number" data-reading-number="${number}">${read(item)?'✓':number}</span><span>${esc(item.title)}${read(item)?'<span class="sr-only"> — lu</span>':''}</span></a></li>`;
  };
  const migrated=progress.migratedThemes?.includes(course.themeId)?'<p class="reading-migration">Vos repères antérieurs sont reportés vers les pages regroupées. « Lu » reste un aide-mémoire personnel.</p>':'';
  return `<aside class="course-sidebar narrative-sidebar"><div class="sidebar-title"><span class="eyebrow">LE PARCOURS PRINCIPAL</span><h2>${esc(course.label)}</h2><p>${counts.read} / ${counts.total} chapitres lus</p><progress max="${counts.total}" value="${counts.read}" aria-label="Lecture du parcours principal"></progress><small>Les huit références restent à consulter selon vos besoins.</small>${migrated}</div><details class="chapter-toc" open><summary>Parcours principal <span>14 chapitres</span></summary><nav aria-label="Parcours principal PyTorch">${course.readingGroups.map(group=>`<section class="toc-reading-group"><h3>${esc(group.title)}</h3><p>${esc(group.description)}</p><ol>${group.chapterIds.map(id=>course.chapters.find(item=>item.id===id)).map(chapterLink).join('')}</ol></section>`).join('')}</nav></details><details class="reference-toc" ${chapter.readingRole==='reference'?'open':''}><summary>Références à la demande <span>8 fiches</span></summary><p>Ouvrez une fiche pour répondre à une difficulté précise. Elle n’ajoute rien au compteur du parcours principal.</p><nav aria-label="Références PyTorch"><ol>${references.map(chapterLink).join('')}</ol></nav></details>${renderDiagnostics(course)}<details class="course-introduction"><summary>Le projet et les prérequis</summary>${course.intro.map(text=>`<p>${esc(text)}</p>`).join('')}<h3>Ce que vous pourrez faire</h3><ul>${course.objectives.map(text=>`<li>${esc(text)}</li>`).join('')}</ul></details></aside>`;
}

export function renderDiagnostics(course){
  const diagnostics=course.diagnostics;
  if(!diagnostics)return '';
  return `<details class="course-diagnostics" id="depannage-pytorch"><summary>${esc(diagnostics.title)}</summary><p>${esc(diagnostics.summary)}</p>${diagnostics.situations.map(situation=>`<details><summary>${esc(situation.title)}</summary><p>${esc(situation.symptom)}</p><pre><code>${esc(situation.check)}</code></pre><p>${esc(situation.explanation)}</p><ul>${situation.links.map(link=>`<li><a href="${courseHref(link.themeId,link.chapterId)}">${esc(link.text)}</a></li>`).join('')}</ul></details>`).join('')}</details>`;
}

export function renderFirstRoute(course,chapter){
  if(!course.readingGroups)return '';
  if(chapter.readingRole==='reference')return `<aside class="first-training-route"><strong>Une référence à consulter quand le besoin apparaît.</strong><p>Pour construire d’abord une boucle et sa validation, <a href="${courseHref(course.themeId,course.readingGroups[0].chapterIds[0])}">reprendre le parcours principal</a>.</p></aside>`;
  if(chapter.id!==course.readingGroups[0].chapterIds[0])return '';
  return `<p class="first-training-route">Les sept premières étapes vont du tableau de trois extraits à une validation. Les lots, les axes et les représentations audio viennent ensuite ; les références peuvent attendre.</p>`;
}
