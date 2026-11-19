import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {readCourses} from '../scripts/validate-courses.mjs';
const courses=await readCourses();
const [generation,audio]=await Promise.all(['audit-generation-research-oral','audit-python-signal-ml'].map(async name=>JSON.parse(await readFile(new URL(`../scripts/verify/${name}-results.json`,import.meta.url),'utf8'))));
const evidence=[...generation.examples.filter(example=>!example.variant),...audio.cases.filter(example=>example.role==='demonstration')];
const find=chapterId=>evidence.find(example=>example.chapterId===chapterId);
const close=(actual,expected,tolerance=1e-6)=>assert.ok(Math.abs(actual-expected)<=tolerance,`${actual} ≠ ${expected}`);

test('les démonstrations des six chapitres audio/génération correspondent à leurs nouvelles preuves CPU',()=>{
  assert.equal(generation.device,'cpu');assert.equal(audio.device,'cpu');
  const ids=['transformer-complet','codecs-neuronaux-rvq','symbolique-midi-et-audio','objectifs-diffusion-et-flow','controle-multimodal-formes','efficacite-petit-budget'];
  for(const id of ids){
    const chapter=courses.flatMap(course=>course.chapters).find(chapter=>chapter.id===id);
    assert.ok(chapter,id);
    const blocks=chapter.blocks.filter(block=>block.code&&(block.language??'python')==='python');
    assert.ok(blocks.length,id);
    for(const block of blocks){
      const hash=createHash('sha256').update(block.code).digest('hex');
      assert.ok(evidence.some(example=>example.chapterId===id&&(example.codeSha256??example.sourceSha256)===hash),`Code affiché sans exécution correspondante : ${id}`);
    }
  }
});

test('modifier le futur préserve les sorties passées sous le masque causal',()=>{
  const {values}=find('transformer-complet');
  assert.equal(values.ecart_causal,0);
  assert.ok(values.ecart_libre>0);
  assert.deepEqual(values.sortie.values[0].slice(0,2),values.causal.values[0].slice(0,2));
  for(const head of values.poids.values[0])for(let query=0;query<head.length;query++){
    close(head[query].reduce((sum,value)=>sum+value,0),1);
    for(let key=query+1;key<head[query].length;key++)assert.equal(head[query][key],0);
  }
});

test('la RVQ et le flux relient les états intermédiaires aux erreurs effectivement calculées',()=>{
  const {values}=find('codecs-neuronaux-rvq');
  assert.deepEqual(values.reconstruction.values,[[1],[-0.75]]);
  let squaredError=0;
  for(let index=0;index<values.z.values.length;index++){
    const residual=values.z.values[index][0]-values.reconstruction.values[index][0];
    close(residual,values.residual.values[index][0]);
    squaredError+=residual**2;
  }
  close(squaredError/values.z.values.length,generation.numericalChecks.rvqMse);
  const flow=find('objectifs-diffusion-et-flow').values;
  close(flow.vitesse_cible.values,flow.x.values-flow.z.values);
  close(flow.point.values,(1-flow.t)*flow.z.values+flow.t*flow.x.values);
  close(flow.point_suivant.values,flow.z.values+flow.pas*flow.vitesse_cible.values);
  close(generation.numericalChecks.flowLongerStep,flow.z.values+0.5*flow.vitesse_cible.values);
});

test('le budget de stockage annoncé provient du nombre de poids et des bits de la quantification',()=>{
  const {values}=find('efficacite-petit-budget');
  assert.equal(values.total,values.d**2);
  assert.equal(values.ajout,2*values.d*values.rang);
  assert.equal(values.octets,Math.ceil(values.total*values.bits/8));
  assert.equal(values.mse_reference,0);
  assert.ok(values.mse>values.mse_reference);
  close(values.echeance_ms,1000*256/48000);
});
