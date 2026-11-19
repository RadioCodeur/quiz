import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {readCourses} from '../scripts/validate-courses.mjs';
import {chapterById} from '../src/course-model.js';

test('la refonte conserve les ancres et sources et documente le déplacement des questions',async()=>{
  const baseline=JSON.parse(await readFile(new URL('../scripts/verify/audit-baseline.json',import.meta.url),'utf8')).courses;
  const moves=JSON.parse(await readFile(new URL('../scripts/verify/audit-question-moves.json',import.meta.url),'utf8'));
  const narrationMoves=JSON.parse(await readFile(new URL('../scripts/verify/pytorch-narration-question-moves.json',import.meta.url),'utf8'));
  const courses=await readCourses();
  for(const [theme,chapters] of Object.entries(baseline)){
    const course=courses.find(course=>course.themeId===theme);assert.ok(course,theme);
    for(const [id,protectedFields] of Object.entries(chapters)){
      const chapter=chapterById(course,id);assert.ok(chapter,`${theme}/${id}`);
      for(const questionId of protectedFields.questionIds){
        const target=narrationMoves.find(move=>move.questionId===questionId)?.chapterId??moves.find(move=>move.questionId===questionId)?.chapterId??id;
        assert.ok(chapterById(course,target)?.questionIds.includes(questionId),`${questionId}: chapitre qui développe la notion`);
      }
      for(const source of protectedFields.sourceIds)assert.ok(chapter.sourceIds.includes(source),`${id}: source ${source}`);
    }
  }
});
