import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {readCourses} from '../scripts/validate-courses.mjs';
const read=name=>readFile(new URL(`../scripts/verify/${name}.json`,import.meta.url),'utf8').then(JSON.parse);
const reports=await Promise.all(['audit-python-signal-ml-results','audit-generation-research-oral-results'].map(read));
const pytorch=await read('narration-pytorch-results');

test('chaque programme Python affiché correspond à une exécution CPU de son chapitre',async()=>{
  const proofs=[];
  assert.equal(pytorch.device,'cpu');
  for(const entry of pytorch.programs)proofs.push({chapterId:entry.chapterId,sha:entry.sha256});
  for(const report of reports){
    assert.equal(report.device,'cpu');
    for(const entry of report.examples??report.cases)proofs.push({chapterId:entry.chapterId??(entry.id??entry.name).split('/')[0],sha:entry.sha256??entry.codeSha256??entry.sourceSha256});
  }
  let blocks=0;
  for(const course of await readCourses())for(const chapter of course.chapters)for(const block of chapter.blocks){
    if(!block.code||(block.language??'python')!=='python')continue;
    blocks++;
    const hash=createHash('sha256').update(block.code).digest('hex');
    if(block.role==='reading-fragment'){
      const proof=pytorch.fragments.find(proof=>proof.chapterId===chapter.id&&proof.sha256===hash&&proof.programId===block.programId);
      assert.ok(proof,`Extrait sans programme exécuté : ${chapter.id}`);
      assert.ok(pytorch.programs.some(program=>program.chapterId===chapter.id&&program.sha256===proof.programSha256));
      assert.deepEqual(proof.sourceLines,block.sourceLines);
    }else assert.ok(proofs.some(proof=>proof.chapterId===chapter.id&&proof.sha===hash),`Sans preuve courante : ${course.themeId}/${chapter.id}`);
    assert.ok(['standalone','excerpt'].includes(block.codeMode));
    if(block.codeMode==='excerpt')assert.ok(block.requires?.length);
  }
  assert.ok(blocks>0);
});
test('la passe arrière reproduit le calcul manuel et la première boucle apprend les trois exemples',()=>{
  const back=pytorch.programs.find(entry=>entry.chapterId==='retropropagation-a-la-main');
  assert.equal(back.values.h.values,6);assert.equal(back.values.y.values,-6);assert.equal(back.values.perte.values,36);
  const gradients=back.stdout.trim().split('\n').at(-1).split(' ').slice(-2).map(Number);
  assert.deepEqual(gradients,[24,-72]);
  const loop=pytorch.programs.find(entry=>entry.chapterId==='premiere-boucle-minimale');
  assert.deepEqual(loop.values.predictions.values,[0,1,0]);
  assert.ok(loop.values.perte_finale.values<.23);
  assert.equal(loop.values.scores_finaux.shape[0],3);
  const validation=pytorch.programs.find(entry=>entry.chapterId==='entrainer-ou-evaluer');
  assert.deepEqual(validation.values.predictions_reserve.values,[0,1,0,1]);
  assert.ok(validation.values.poids_identiques&&validation.values.biais_identiques);
  assert.equal(validation.values.scores_reserve.requiresGrad,false);
});
