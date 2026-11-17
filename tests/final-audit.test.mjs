import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {readCourses} from '../scripts/validate-courses.mjs';
import {auditChapter,auditModule} from '../scripts/audit-prose.mjs';
import {QUICK_CHAPTERS,REVISION_WEEKS} from '../src/revision-path.js';
const courses=await readCourses();
const read=name=>readFile(new URL(`../scripts/verify/${name}.json`,import.meta.url),'utf8').then(JSON.parse);

test('la prose de chaque chapitre est courte, conclue à l’oral et justifie toute exception de longueur',()=>{
  for(const course of courses){
    assert.deepEqual(auditModule(course),[],course.themeId);
    for(const chapter of course.chapters){
    const audit=auditChapter(course,chapter);
    assert.deepEqual(audit.longSentences,[],`${course.themeId}/${chapter.id}`);
    assert.ok(audit.interviewEnding,chapter.id);
    assert.ok(audit.words<=1100||audit.lengthJustification?.trim(),chapter.id);
    }
  }
});

test('le parcours rapide contient des conditions explicites et quatre semaines reliées aux vrais chapitres',()=>{
  const valid=link=>courses.some(course=>course.themeId===link.themeId&&course.chapters.some(chapter=>chapter.id===link.chapterId));
  assert.equal(REVISION_WEEKS.length,4);
  assert.ok(QUICK_CHAPTERS.some(chapter=>chapter.themeId==='python-scientifique'));
  assert.ok(QUICK_CHAPTERS.some(chapter=>chapter.themeId==='audio-signal'));
  for(const chapter of QUICK_CHAPTERS)assert.ok(valid(chapter)&&chapter.condition.startsWith('Si '));
  for(const week of REVISION_WEEKS)assert.ok(week.goal&&week.deliverable&&week.links.every(valid));
  assert.equal(REVISION_WEEKS[0].links[0].themeId,'pytorch');
  assert.equal(REVISION_WEEKS.at(-1).links.at(-1).themeId,'entretien');
});

test('chaque bloc Python possède une preuve d’exécution CPU correspondant exactement à son contenu',async()=>{
  const [existing,added,corpus,attention,codecs,diffusion]=await Promise.all(['pytorch-existing-results','pytorch-additions-results','existing-corpus-results','b-attention-control-results','b-codecs-symbolic-results','b-diffusion-efficiency-results'].map(read));
  assert.equal(corpus.findings.length,0);
  for(const report of [existing,added,corpus,attention,codecs,diffusion])assert.equal(report.device,'cpu');
  const hashes=new Set([
    ...existing.records.map(record=>record.sha256),...Object.values(added.examples).map(entry=>entry.codeSha256),
    ...corpus.examples.map(entry=>entry.source_sha256),...attention.cases.map(entry=>entry.sha256),
    ...Object.values(codecs.examples).map(entry=>entry.codeSha256),...Object.values(diffusion.examples).map(entry=>entry.codeSha256),
  ]);
  let count=0;
  for(const course of courses)for(const chapter of course.chapters)for(const block of chapter.blocks){
    if(block.code&&(block.language??'python')==='python'){
      count++;
      assert.ok(hashes.has(createHash('sha256').update(block.code).digest('hex')),`Sans preuve : ${course.themeId}/${chapter.id}`);
    }
  }
  assert.ok(count>=60);
});
