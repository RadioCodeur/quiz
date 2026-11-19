import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {readCourses} from '../scripts/validate-courses.mjs';
import {chapterById,readingChapters,readingProgress,normalizeProgress} from '../src/course-model.js';
const courses=await readCourses(),course=courses.find(course=>course.themeId==='pytorch');
const baseline=JSON.parse(await readFile(new URL('../scripts/verify/pytorch-narration-baseline.json',import.meta.url),'utf8'));

test('la refonte PyTorch préserve exactement les sept autres textes et toutes les anciennes destinations',async()=>{
  for(const [id,sha]of Object.entries(baseline.otherModules)){
    const source=(await readFile(new URL(`../public/courses/${id}.json`,import.meta.url),'utf8')).replace(/\r\n/g,'\n');
    assert.equal(createHash('sha256').update(source).digest('hex'),sha,id);
  }
  for(const old of baseline.pytorch){
    const target=chapterById(course,old.id);assert.ok(target,old.id);
    for(const source of old.sourceIds)assert.ok(target.sourceIds.includes(source),`${old.id}: source conservée`);
  }
});
test('le trajet vers la validation exclut les références et les anciens repères peuvent tous être repris',()=>{
  const main=readingChapters(course),references=course.chapters.filter(chapter=>chapter.readingRole==='reference');
  assert.equal(main.length,14);assert.equal(references.length,8);
  assert.equal(main[6].id,'entrainer-ou-evaluer');
  assert.deepEqual(course.readingGroups.flatMap(group=>group.chapterIds),main.map(chapter=>chapter.id));
  const migrated=normalizeProgress({completed:baseline.pytorch.map(chapter=>'pytorch/'+chapter.id),last:{themeId:'pytorch',chapterId:'moyennes-masquees'}},courses);
  assert.deepEqual(readingProgress(course,migrated),{read:14,total:14});
  assert.equal(migrated.completed.length,22);assert.equal(migrated.last.chapterId,'padding-et-collate');
  assert.deepEqual(readingProgress(course,{completed:references.map(chapter=>'pytorch/'+chapter.id)}),{read:0,total:14});
});
test('le code du fil et son complément autonome restent accessibles avec des responsabilités distinctes',()=>{
  for(const chapter of course.chapters){
    const fragments=chapter.blocks.filter(block=>block.role==='reading-fragment');
    assert.ok(fragments.length,chapter.id);
    for(const fragment of fragments){
      const program=chapter.blocks.find(block=>block.readingCompanion&&block.programId===fragment.programId);
      assert.ok(program&&program.disclosure===true&&program.codeMode==='standalone',chapter.id);
      const [start,end]=fragment.sourceLines;
      assert.equal(fragment.code.replace(/\n$/,''),program.code.split('\n').slice(start-1,end).join('\n').replace(/\n$/,''));
    }
  }
});
