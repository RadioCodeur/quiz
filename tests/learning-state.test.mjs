import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeProgress,checkpointSignature,setChapterReview,setChapterRead} from '../src/course-model.js';
const checkpoint={prompt:'Une forme ?',correctOptionId:'b',options:['a','b','c','d'].map(id=>({id,text:id}))};
const course={themeId:'pytorch',chapters:[{id:'axes',checkpoint,blocks:[{type:'walkthrough',steps:[{},{}]}]}]};
const key='pytorch/axes';
test('les anciens repères migrent et les nouveaux états de lecture sont validés',()=>{
  const old=normalizeProgress({completed:[key],last:{themeId:'pytorch',chapterId:'axes'}},[course]);
  assert.deepEqual(old.completed,[key]);assert.deepEqual(old.review,[]);
  const raw={...old,review:[key,'inconnu'],chapterStates:{[key]:{walkthroughs:{'walk-0':99},scrollY:1200,chosenId:'a',optionOrder:['d','b','a','c'],checkpointSignature:checkpointSignature(checkpoint)}}};
  const restored=normalizeProgress(raw,[course]);
  assert.equal(restored.chapterStates[key].walkthroughs['walk-0'],1);
  assert.equal(restored.chapterStates[key].chosenId,'a');assert.equal(restored.chapterStates[key].scrollY,1200);
  assert.deepEqual(restored.review,[key]);
});
test('une ancienne réponse ne se transforme pas en tentative sur une question réécrite',()=>{
  const raw={chapterStates:{[key]:{chosenId:'a',optionOrder:['a','b','c','d'],checkpointSignature:'ancienne question'}}};
  const restored=normalizeProgress(raw,[course]);assert.equal(restored.chapterStates[key].chosenId,undefined);
});
test('à revoir reste distinct de lu et conserve les autres réglages',()=>{
  const initial=normalizeProgress(null,[course]);
  const review=setChapterReview(initial,'pytorch','axes',true);
  assert.deepEqual(review.review,[key]);assert.deepEqual(review.completed,[]);
  const read=setChapterRead(review,'pytorch','axes',true);
  assert.deepEqual(read.completed,[key]);assert.deepEqual(read.review,[key]);
  assert.deepEqual(setChapterReview(read,'pytorch','axes',false).review,[]);
});
