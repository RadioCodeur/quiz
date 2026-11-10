import test from 'node:test';
import assert from 'node:assert/strict';
import { readCourses,validateCourses } from '../scripts/validate-courses.mjs';
import { readBank } from '../scripts/read-bank.mjs';
import { buildCoverage, normalizeProgress, resolveChapter, setChapterRead, courseHref, chapterMinutes, chapterText, mergeCourseReferences, courseStage } from '../src/course-model.js';
import { readFile } from 'node:fs/promises';
import { plotGeometry, renderPlot, renderVisual, renderWalkthrough, renderCheckpoint, renderFirstExample } from '../src/learning-blocks.js';
const courses=await readCourses();
const data=await readBank();

test('cours : schéma, ordre pédagogique, sources et couverture des 200 questions',()=>{
  assert.equal(validateCourses(courses,data).coveredQuestions,200);
});
test('cours : chaque lien du quiz arrive dans le chapitre qui couvre sa question',()=>{
  const coverage=buildCoverage(courses);
  for(const q of data.bank) {
    const entry=coverage.get(q.id);
    const course=courses.find(c=>c.themeId===q.primaryTheme);
    assert.equal(resolveChapter(course,{questionId:q.id}).id,entry.chapterId);
    const url=new URL(courseHref(q.primaryTheme,null,q.id),'https://example.test/quiz/');
    assert.equal(url.pathname,'/quiz/cours.html');
    assert.equal(url.searchParams.get('question'),q.id);
  }
});
test('cours : ancres de chapitres et repli des liens périmés',()=>{
  const course=courses[0],chapter=course.chapters[1];
  assert.equal(resolveChapter(course,{chapterId:chapter.id}),chapter);
  assert.equal(resolveChapter(course,{chapterId:'ancien',questionId:'retire'}),course.chapters[0]);
  assert.equal(new URL(courseHref(course.themeId,chapter.id),'https://test/quiz/').hash,`#${chapter.id}`);
  assert.ok(chapterMinutes(chapter)>=3);
});
test('cours : progression corrompue filtrée, sans perdre les repères valides',()=>{
  const c=courses[0],ch=c.chapters[0],key=`${c.themeId}/${ch.id}`;
  const result=normalizeProgress({completed:[key,key,'obsolete',{},null],last:{themeId:c.themeId,chapterId:ch.id},readingMode:true,largeText:'yes'},courses);
  assert.deepEqual(result.completed,[key]);
  assert.equal(result.readingMode,true);
  assert.equal(result.largeText,false);
  assert.deepEqual(result.last,{themeId:c.themeId,chapterId:ch.id});
  assert.equal(normalizeProgress({last:{themeId:'absent',chapterId:'absent'}},courses).last,null);
  assert.deepEqual(normalizeProgress(null,courses).completed,[]);
});
test('cours : marquer et démarquer un chapitre sans modifier la session de quiz',()=>{
  const c=courses[0],ch=c.chapters[0],progress=normalizeProgress(null,courses);
  const marked=setChapterRead(progress,c.themeId,ch.id,true);
  assert.equal(progress.completed.length,0);
  assert.equal(setChapterRead(marked,c.themeId,ch.id,true).completed.length,1);
  assert.equal(setChapterRead(marked,c.themeId,ch.id,false).completed.length,0);
});

test('la refonte conserve les anciens liens et repères des 57 chapitres',async()=>{
  const previous=JSON.parse(await readFile(new URL('./fixtures/course-ids-v1.json',import.meta.url),'utf8'));
  for(const course of courses)for(const id of previous[course.themeId])assert.ok(course.chapters.some(ch=>ch.id===id),`${course.themeId}/${id}`);
});
test('la destination annoncée du cours couvre tout le chemin sans saut de chapitre',()=>{
  for(const course of courses){
    assert.deepEqual(course.journey.stages.flatMap(stage=>stage.chapterIds),course.chapters.map(ch=>ch.id));
    for(const chapter of course.chapters)assert.ok(courseStage(course,chapter.id).chapterIds.includes(chapter.id));
  }
});
test('les nouvelles références techniques sont fusionnées sans perdre les références du quiz',()=>{
  const result=mergeCourseReferences(data.sources,courses),ids=new Set(result.map(source=>source.id));
  assert.equal(result.length,ids.size);
  for(const course of courses)for(const chapter of course.chapters)for(const id of chapter.sourceIds)assert.ok(ids.has(id));
  assert.ok(result.length>data.sources.length);
});
test('les durées comprennent les étapes expliquées, pas seulement les paragraphes',()=>{
  const chapter={blocks:[{type:'walkthrough',title:'Exemple',goal:'Comprendre',steps:[{title:'Première étape',text:'observer '.repeat(600)}],result:'Interpréter'}],context:{problem:'Un problème'}};
  assert.ok(chapterText(chapter).includes('observer'));
  assert.ok(chapterMinutes(chapter)>=5);
});
test('les graphiques conservent le sens des axes, y compris les séries constantes',()=>{
  const graph={title:'Valeurs',xLabel:'Temps (s)',yLabel:'Amplitude',caption:'Exemple pédagogique',series:[{name:'signal',points:[[0,-1],[1,1]]}]};
  const geometry=plotGeometry(graph);
  assert.ok(geometry.x(0)<geometry.x(1));
  assert.ok(geometry.y(-1)>geometry.y(1));
  const constant=plotGeometry({...graph,series:[{name:'constante',points:[[1,2],[1,2]]}]});
  assert.ok(Number.isFinite(constant.x(1))&&Number.isFinite(constant.y(2)));
  const rendered=renderPlot(graph,'test');
  assert.ok(rendered.includes('Temps (s)')&&rendered.includes('Lire les valeurs du graphique'));
});
test('les exemples guidés surlignent les vraies lignes et échappent le contenu',()=>{
  const example={title:'Exemple',goal:'Suivre les objets',code:'x = 1\nprint(x)',steps:[{title:'Affecter',text:'Associer un nom',lines:[1],state:'x = 1'},{title:'Observer',text:'Lire une valeur',lines:[2]},{title:'Conclure',text:'Interpréter'}],result:'Une valeur < un seuil'};
  const rendered=renderWalkthrough(example,'sample');
  assert.ok(rendered.includes('walk-code-line is-active'));
  assert.ok(rendered.includes('data-line="1"'));
  assert.ok(rendered.includes('Une valeur &lt; un seuil'));
  const visual=renderVisual({kind:'flow',title:'<script>',nodes:[{title:'A',text:'Entrée'},{title:'B',text:'Sortie'}],caption:'Un flux'});
  assert.ok(visual.includes('&lt;script&gt;')&&!visual.includes('<script>'));
});
test('les QCM de transfert restent à quatre options avec des IDs indépendants de la position',()=>{
  for(const course of courses)for(const chapter of course.chapters){
    const rendered=renderCheckpoint(chapter.checkpoint);
    assert.equal((rendered.match(/data-checkpoint-option=/g)??[]).length,4);
    assert.ok(rendered.includes(`data-checkpoint-option="${chapter.checkpoint.correctOptionId}"`));
  }
});

test('chaque module annonce ses notions dans l’ordre des chapitres',()=>{
  for(const course of courses){
    assert.ok(course.moduleIntroduction.startingPoint&&course.moduleIntroduction.goal);
    const indices=course.moduleIntroduction.concepts.map(concept=>course.chapters.findIndex(ch=>ch.id===concept.chapterId));
    assert.ok(indices.every(index=>index>=0));
    assert.deepEqual(indices,[...indices].sort((a,b)=>a-b));
    assert.ok(course.chapters.every(ch=>ch.notions.length>=2&&ch.notions.every(n=>n.name&&n.explanation)));
  }
});
test('le petit exemple et sa sortie précèdent l’application complète',()=>{
  for(const course of courses)for(const chapter of course.chapters){
    const index=chapter.blocks.findIndex(block=>block.type==='first-example');
    assert.ok(index>=0&&index<=3);
    assert.ok(index<chapter.blocks.findIndex(block=>block.type==='walkthrough'));
    const block=chapter.blocks[index];
    assert.ok(block.output&&block.explanation&&block.variant.change&&block.variant.output&&block.variant.explanation);
    assert.ok(block.code.split('\n').length<=6);
  }
});
test('les sorties et les variantes du premier exemple restent du texte lisible',()=>{
  const rendered=renderFirstExample({title:'Un exemple',introduction:'Lire une valeur',language:'python',code:'print(3 < 4)',output:'True',explanation:'Une comparaison',variant:{change:'Remplacer 4 par 2',output:'False',explanation:'3 est supérieur à 2.'}});
  assert.ok(rendered.includes('print(3 &lt; 4)'));
  assert.ok(rendered.includes('Résultat expliqué')&&rendered.includes('True'));
  assert.ok(rendered.includes('Changeons une seule chose')&&rendered.includes('False'));
});
