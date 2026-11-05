import test from 'node:test';
import assert from 'node:assert/strict';
import { readCourses,validateCourses } from '../scripts/validate-courses.mjs';
import { readBank } from '../scripts/read-bank.mjs';
import { buildCoverage, normalizeProgress, resolveChapter, setChapterRead, courseHref, chapterMinutes } from '../src/course-model.js';
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
