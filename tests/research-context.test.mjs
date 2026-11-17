import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {readCourses} from '../scripts/validate-courses.mjs';
const courses=await readCourses();
const context=courses.find(course=>course.themeId==='contexte-recherche');
const registry=JSON.parse(await readFile(new URL('../scripts/verify/research-sources.json',import.meta.url),'utf8'));

test('chaque section de contexte relie des mécanismes techniques sans créer un thème de quiz',()=>{
  assert.equal(context.kind,'context');
  assert.equal(context.chapters.length,4);
  for(const chapter of context.chapters){
    assert.equal(chapter.questionIds.length,0);
    assert.ok(chapter.blocks.some(block=>block.links?.some(link=>link.themeId!=='contexte-recherche')));
    for(const id of chapter.sourceIds){
      const ref=context.references.find(source=>source.id===id);
      assert.ok(registry.sources.some(source=>source.opened&&source.url===ref.url),ref.url);
    }
  }
});
test('huit lectures ont chacune trois idées et une question de recherche',()=>{
  const chapter=context.chapters.find(chapter=>chapter.id==='huit-lectures-pour-discuter');
  const indices=chapter.blocks.flatMap((block,i)=>block.type==='heading'?[i]:[]);
  assert.equal(indices.length,8);
  for(const index of indices){
    assert.equal(chapter.blocks[index+1].items.length,3);
    assert.ok(chapter.blocks[index+2].text.startsWith('Question à poser :'));
  }
});
