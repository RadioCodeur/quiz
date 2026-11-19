import test from 'node:test';
import assert from 'node:assert/strict';
import {chapterById,resolveChapter,normalizeProgress,readingProgress,chapterNavigation,chapterPosition,checkpointSignature} from '../src/course-model.js';
import {renderWalkthrough,renderCheckpoint} from '../src/learning-blocks.js';
const checkpoint={taskTitle:'Prévoyez le sens du pas',prompt:'Quel sens ?',explanation:'Le signe du gradient indique le déplacement.',correctOptionId:'a',options:['a','b','c','d'].map(id=>({id,text:id}))};
const chapters=[{id:'first',questionIds:['pt-a'],blocks:[{id:'main',type:'walkthrough',steps:[{},{}]}],checkpoint},{id:'second',questionIds:['pt-b'],blocks:[],checkpoint},{id:'reference',readingRole:'reference',questionIds:[],blocks:[]}];
const course={themeId:'pytorch',chapters,chapterAliases:{'old-first':'first','old-second':'second'},readingGroups:[{title:'Construire la boucle',chapterIds:['first','second']}]};

test('les anciennes ancres ont une destination réelle avant le repli des liens inconnus',()=>{
  assert.equal(chapterById(course,'old-second'),chapters[1]);
  assert.equal(resolveChapter(course,{chapterId:'old-second'}),chapters[1]);
  assert.equal(resolveChapter(course,{chapterId:'absent',questionId:'pt-b'}),chapters[1]);
  assert.equal(chapterById(course,'absent'),undefined);
});
test('les repères regroupés, la dernière lecture et les réponses compatibles migrent sans doublon',()=>{
  const raw={completed:['pytorch/old-first','pytorch/first','pytorch/reference','absent'],review:['pytorch/old-second'],last:{themeId:'pytorch',chapterId:'old-second'},readingMode:true,largeText:true,chapterStates:{'pytorch/old-first':{walkthroughs:{main:99},scrollY:300,chosenId:'a',checkpointSignature:checkpointSignature(checkpoint)}}};
  const migrated=normalizeProgress(raw,[course]);
  assert.deepEqual(migrated.completed,['pytorch/first','pytorch/reference']);
  assert.deepEqual(migrated.last,{themeId:'pytorch',chapterId:'second'});
  assert.deepEqual(migrated.review,['pytorch/second']);
  assert.equal(migrated.chapterStates['pytorch/first'].chosenId,'a');
  assert.equal(migrated.chapterStates['pytorch/first'].walkthroughs.main,1);
  assert.ok(migrated.readingMode&&migrated.largeText);assert.deepEqual(migrated.migratedThemes,['pytorch']);
  assert.deepEqual(normalizeProgress(migrated,[course]),migrated);
});
test('consulter une référence ne fait pas avancer la barre du parcours principal',()=>{
  assert.deepEqual(readingProgress(course,{completed:['pytorch/reference']}),{read:0,total:2});
  assert.deepEqual(readingProgress(course,{completed:['pytorch/reference','pytorch/first']}),{read:1,total:2});
  assert.deepEqual(chapterNavigation(course,chapters[1]),{previous:chapters[0],next:null});
  assert.deepEqual(chapterNavigation(course,chapters[2]),{previous:null,next:null});
  assert.deepEqual(chapterPosition(course,chapters[2]),{position:1,total:1,reference:true});
});
test('une décomposition garde ses lignes exactes à côté de l’explication et un titre adapté à son état',()=>{
  const rendered=renderWalkthrough({title:'Premier pas',goal:'Déplacer',code:'w = 0\nw = 0.4',readingCompanion:true,steps:[{title:'Appliquer',text:'Le poids change.',lines:[2],state:'w = 0.4',stateLabel:'Le poids après le pas'}],result:'La nouvelle perte se recalcule.'},'test');
  assert.ok(rendered.includes('class="current-code-lines"'));
  assert.ok(rendered.includes('current-line-number">2</span>w = 0.4'));
  assert.ok(rendered.includes('Le poids après le pas'));
  assert.ok(!rendered.includes('Valeurs et formes à cette étape'));
  assert.ok(renderCheckpoint(checkpoint).includes('<h2>Prévoyez le sens du pas</h2>'));
});
