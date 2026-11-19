import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {calculateLab,renderTensorLab} from '../src/tensor-labs.js';
import {renderCodePreparation} from '../src/learning-blocks.js';
const evidence=JSON.parse(await readFile(new URL('../scripts/verify/narration-pytorch-results.json',import.meta.url),'utf8'));
const values=id=>evidence.programs.find(example=>example.chapterId===id).values;

test('les axes et déplacements visibles concordent avec les calculs PyTorch exécutés',()=>{
  assert.deepEqual(calculateLab('axes',{axis:1}).result,values('du-pipeline-au-modele').predictions.values);
  assert.deepEqual(calculateLab('axes',{axis:0}).result,[1,0]);
  const view=calculateLab('reshape',{value:4}),proof=values('organiser-les-axes');
  assert.deepEqual(view.reshape,proof.redecoupe.values);assert.deepEqual(view.transpose,proof.transpose.values);
  assert.equal(view.reshape[1][1],view.transpose[0][1]);
});
test('changer un poids ou une référence modifie le résultat numérique correspondant',()=>{
  const base=calculateLab('linear'),changed=calculateLab('linear',{w0:10,w1:1,bias:0});
  assert.equal(base.result,1.5);assert.equal(changed.result,2.5);
  assert.deepEqual(changed.products,[1,1.5]);
  const broadcast=calculateLab('broadcast',{r0:1,r1:2});
  assert.deepEqual(broadcast.result,[[0,0],[2,2],[4,4]]);
  assert.deepEqual(broadcast.matrix,[[1,2],[3,4],[5,6]]);
  const input=values('selection-diffusion-reduction').X.values;
  const reference=values('selection-diffusion-reduction').reference.values[0];
  const actual=calculateLab('broadcast',{}, {input,reference});
  const expected=values('selection-diffusion-reduction').centres.values;
  actual.result.flat().forEach((value,index)=>assert.ok(Math.abs(value-expected.flat()[index])<1e-6));
});
test('le grand pas peut augmenter la perte et le minimum reste fixe',()=>{
  const usual=calculateLab('gradient',{weight:0,rate:.1});
  assert.equal(usual.next,.4);assert.ok(Math.abs(usual.nextLoss-2.56)<1e-12);
  const large=calculateLab('gradient',{weight:0,rate:1.1});
  assert.equal(large.next,4.4);assert.ok(large.nextLoss>large.loss);
  const minimum=calculateLab('gradient',{weight:2,rate:1.1});assert.equal(minimum.next,2);assert.equal(minimum.nextLoss,0);
});
test('le masque corrige le dénominateur et Conv2d applique le noyau sans retournement',()=>{
  assert.deepEqual(calculateLab('padding',{masked:true}).result,[3,6]);
  assert.deepEqual(calculateLab('padding',{masked:false}).result,[3,3]);
  assert.deepEqual(calculateLab('conv',{position:0}).products,[[1,0],[0,-5]]);
  assert.deepEqual(calculateLab('conv',{position:3}).output,[[-4,-4],[-4,-4]]);
  const sourceKernel=[[1,0],[0,-1]];
  assert.deepEqual(calculateLab('conv',{w00:2},{kernel:sourceKernel}).output,[[-3,-2],[0,1]]);
  assert.deepEqual(sourceKernel,[[1,0],[0,-1]],'La manipulation ne change pas le noyau de référence');
});
test('les ressources restent sous le répertoire Pages et les textes restent échappés',()=>{
  const html=renderCodePreparation({codeMode:'excerpt',requires:['x < y'],resources:[{label:'Voix',path:'media/audio/voice-original.wav'}]},'/quiz/');
  assert.ok(html.includes('/quiz/media/audio/voice-original.wav'));assert.ok(html.includes('x &lt; y'));
  assert.throws(()=>renderCodePreparation({resources:[{label:'Sortie',path:'media/../secret'}]}));
  const lab=renderTensorLab({kind:'axes',title:'<script>',caption:'Des scores'},'safe');
  assert.ok(lab.includes('&lt;script&gt;'));assert.ok(lab.includes('sans interpréteur Python'));
});
