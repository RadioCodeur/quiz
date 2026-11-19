import test from 'node:test';
import assert from 'node:assert/strict';
import {readCourses} from '../scripts/validate-courses.mjs';
import {QUICK_CHAPTERS,REVISION_WEEKS} from '../src/revision-path.js';
import {chapterById,readingChapters} from '../src/course-model.js';
const courses=await readCourses();

test('la première boucle précède les données variables et les prérequis restent accessibles',()=>{
  const course=courses.find(course=>course.themeId==='pytorch');
  const index=id=>course.chapters.findIndex(chapter=>chapter.id===id);
  assert.ok(index('premiere-boucle-minimale')<index('dataset-et-batches'));
  assert.ok(index('dataset-et-batches')<index('padding-et-collate'));
  assert.ok(index('organiser-les-axes')<index('padding-et-collate'));
  assert.equal(chapterById(course,'moyennes-masquees').id,'padding-et-collate');
  assert.ok(index('convolution-a-la-main')<index('conv-mel-autoencodeur'));
  const main=readingChapters(course);
  assert.equal(main.length,14);assert.equal(course.chapters.length-main.length,8);
  assert.equal(main[6].id,'entrainer-ou-evaluer');
  assert.ok(index('autograd-et-derivees')<index('premiere-boucle-minimale'));
  assert.ok(index('premiere-boucle-minimale')<index('retropropagation-a-la-main'));
  for(const chapter of course.chapters)for(const link of chapter.prerequisites??[])assert.ok(courses.some(c=>c.themeId===link.themeId&&chapterById(c,link.chapterId)));
});
test('le parcours de révision relie les priorités à des chapitres existants',()=>{
  const valid=link=>courses.some(course=>course.themeId===link.themeId&&chapterById(course,link.chapterId));
  assert.equal(REVISION_WEEKS.length,4);
  for(const chapter of QUICK_CHAPTERS)assert.ok(valid(chapter)&&chapter.condition);
  for(const week of REVISION_WEEKS)assert.ok(week.goal&&week.deliverable&&week.links.every(valid));
  assert.equal(REVISION_WEEKS[0].links[0].themeId,'pytorch');
  assert.ok(!REVISION_WEEKS[0].links.some(link=>chapterById(courses.find(c=>c.themeId===link.themeId),link.chapterId).readingRole==='reference'));
  assert.equal(REVISION_WEEKS.at(-1).links.at(-1).themeId,'entretien');
});
