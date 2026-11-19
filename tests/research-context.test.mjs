import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {readCourses} from '../scripts/validate-courses.mjs';
const courses=await readCourses();
const context=courses.find(course=>course.themeId==='contexte-recherche');
const registry=JSON.parse(await readFile(new URL('../scripts/verify/research-sources.json',import.meta.url),'utf8'));

test('chaque section de contexte relie des mécanismes techniques sans créer un thème de quiz',()=>{
  assert.equal(context.kind,'context');
  assert.ok(context.chapters.length);
  for(const chapter of context.chapters){
    assert.equal(chapter.questionIds.length,0);
    const links=chapter.blocks.flatMap(block=>block.links??[]);
    assert.ok(links.some(link=>link.themeId!=='contexte-recherche'));
    for(const link of links)assert.ok(courses.some(course=>course.themeId===link.themeId&&course.chapters.some(chapter=>chapter.id===link.chapterId)),`${chapter.id} → ${link.themeId}/${link.chapterId}`);
    for(const id of chapter.sourceIds){
      const ref=context.references.find(source=>source.id===id);
      assert.ok(registry.sources.some(source=>source.opened&&source.url===ref.url),ref.url);
    }
  }
});
test('les huit lectures vérifiées gardent une fiche et une question qui leur sont associées',()=>{
  const chapter=context.chapters.find(chapter=>chapter.id==='huit-lectures-pour-discuter');
  assert.equal(registry.readingList.length,8);
  const questions=[];
  for(const reading of registry.readingList){
    const index=chapter.blocks.findIndex(block=>block.type==='heading'&&block.text===reading.title);
    assert.ok(index>=0,reading.title);
    const following=chapter.blocks.slice(index+1);
    const boundary=following.findIndex(block=>block.type==='heading');
    const section=boundary<0?following:following.slice(0,boundary);
    assert.ok(section.some(block=>block.type==='list'&&block.items.length>=2),reading.title);
    const question=section.find(block=>block.type==='paragraph'&&block.text.startsWith('Question à poser :'));
    assert.ok(question,reading.title);
    questions.push(question.text);
    const source=registry.sources.find(source=>source.id===reading.sourceId);
    assert.ok(source?.opened&&context.references.some(ref=>chapter.sourceIds.includes(ref.id)&&ref.url===source.url),reading.title);
  }
  assert.equal(new Set(questions).size,8);
});
