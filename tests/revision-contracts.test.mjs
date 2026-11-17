import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {readCourses} from '../scripts/validate-courses.mjs';

test('la révision conserve tous les liens, associations et checkpoints des 65 chapitres initiaux',async()=>{
  const baseline=JSON.parse(await readFile(new URL('../scripts/verify/baseline-course-contracts.json',import.meta.url),'utf8'));
  const courses=await readCourses();
  for(const [theme,chapters] of Object.entries(baseline)){
    const course=courses.find(course=>course.themeId===theme);assert.ok(course,theme);
    for(const [id,protectedFields] of Object.entries(chapters)){
      const chapter=course.chapters.find(chapter=>chapter.id===id);assert.ok(chapter,`${theme}/${id}`);
      assert.deepEqual(chapter.questionIds,protectedFields.questionIds,`${id}: questions`);
      assert.deepEqual(chapter.checkpoint,protectedFields.checkpoint,`${id}: checkpoint`);
      for(const source of protectedFields.sourceIds)assert.ok(chapter.sourceIds.includes(source),`${id}: source ${source}`);
    }
  }
});
