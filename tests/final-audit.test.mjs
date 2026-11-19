import test from 'node:test';
import assert from 'node:assert/strict';
import {readCourses} from '../scripts/validate-courses.mjs';
import {QUICK_CHAPTERS,REVISION_WEEKS} from '../src/revision-path.js';
const courses=await readCourses();

test('la première boucle précède les données variables et les prérequis restent accessibles',()=>{
  const course=courses.find(course=>course.themeId==='pytorch');
  const index=id=>course.chapters.findIndex(chapter=>chapter.id===id);
  assert.ok(index('premiere-boucle-minimale')<index('dataset-et-batches'));
  assert.ok(index('dataset-et-batches')<index('padding-et-collate'));
  assert.ok(index('ajouter-retirer-un-axe')<index('padding-et-collate'));
  assert.ok(index('padding-et-collate')<index('moyennes-masquees'));
  assert.ok(index('convolution-a-la-main')<index('conv-mel-autoencodeur'));
  assert.ok(index('optimiseurs-regularisation-pratique')<index('sauvegarder-et-reprendre'));
  for(const chapter of course.chapters)for(const link of chapter.prerequisites??[])assert.ok(courses.some(c=>c.themeId===link.themeId&&c.chapters.some(ch=>ch.id===link.chapterId)));
});
test('le parcours de révision relie les priorités à des chapitres existants',()=>{
  const valid=link=>courses.some(course=>course.themeId===link.themeId&&course.chapters.some(chapter=>chapter.id===link.chapterId));
  assert.equal(REVISION_WEEKS.length,4);
  for(const chapter of QUICK_CHAPTERS)assert.ok(valid(chapter)&&chapter.condition);
  for(const week of REVISION_WEEKS)assert.ok(week.goal&&week.deliverable&&week.links.every(valid));
  assert.equal(REVISION_WEEKS[0].links[0].themeId,'pytorch');
  assert.equal(REVISION_WEEKS.at(-1).links.at(-1).themeId,'entretien');
});
