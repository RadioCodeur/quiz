import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {readCourses} from '../scripts/validate-courses.mjs';
const courses=await readCourses();
const reports=await Promise.all(['b-attention-control','b-codecs-symbolic','b-diffusion-efficiency'].map(async name=>JSON.parse(await readFile(new URL(`../scripts/verify/${name}-results.json`,import.meta.url),'utf8'))));

test('les six nouveaux exemples audio/génération affichent exactement le code exécuté sur CPU',()=>{
  let count=0;
  for(const report of reports){
    assert.equal(report.device,'cpu');
    const entries=report.cases??Object.entries(report.examples).map(([chapterId,value])=>({chapterId,...value}));
    for(const entry of entries){
      const chapter=courses.flatMap(c=>c.chapters).find(ch=>ch.id===entry.chapterId);
      assert.ok(chapter,entry.chapterId);
      const code=chapter.blocks.filter(b=>b.code&&b.language!=='text').map(b=>b.code);
      assert.equal(code.length,1,entry.chapterId);
      assert.equal(createHash('sha256').update(code[0]).digest('hex'),entry.sha256??entry.codeSha256);
      assert.ok(entry.stdout.trim());count++;
    }
  }
  assert.equal(count,6);
});

test('le masque conserve le passé et les coûts restent distincts d’une qualité audio mesurée',()=>{
  const transformer=reports[0].cases.find(e=>e.chapterId==='transformer-complet');
  assert.equal(transformer.metrics.causalPastDifference,0);
  assert.ok(transformer.metrics.unmaskedPastDifference>0);
  const efficiency=reports[2].examples['efficacite-petit-budget'];
  assert.ok(efficiency.quantization[0].mse<efficiency.quantization[1].mse);
  assert.ok(efficiency.quantization[0].logicalWeightBytes>efficiency.quantization[1].logicalWeightBytes);
  assert.ok(reports[2].limits.some(text=>text.includes('aucun noyau entier')));
});
