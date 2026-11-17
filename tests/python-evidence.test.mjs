import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {readCourses} from '../scripts/validate-courses.mjs';
const digest=code=>createHash('sha256').update(code).digest('hex');

test('les vingt chapitres PyTorch possèdent des preuves CPU liées au code affiché',async()=>{
  const course=(await readCourses()).find(course=>course.themeId==='pytorch');
  const [existing,added]=await Promise.all(['pytorch-existing-results','pytorch-additions-results'].map(async name=>JSON.parse(await readFile(new URL(`../scripts/verify/${name}.json`,import.meta.url),'utf8'))));
  assert.equal(existing.device,'cpu');assert.equal(added.device,'cpu');
  const proofs=new Set([...existing.records.map(record=>record.sha256),...Object.values(added.examples).map(example=>example.codeSha256)]);
  assert.equal(course.chapters.length,20);
  for(const chapter of course.chapters){
    const blocks=chapter.blocks.filter(block=>block.code&&(block.language??'python')==='python');
    assert.ok(blocks.length,chapter.id);
    for(const block of blocks)assert.ok(proofs.has(digest(block.code)),`Code sans preuve à jour : ${chapter.id}`);
  }
});
test('la rétropropagation demandée garde ses deux poids et ses gradients exécutés',async()=>{
  const report=JSON.parse(await readFile(new URL('../scripts/verify/pytorch-additions-results.json',import.meta.url),'utf8'));
  const output=report.examples['retropropagation-a-la-main'].stdout;
  assert.ok(output.includes('6.0 -6.0 36.0'));
  assert.ok(output.includes('-12.0 12.0'));
  assert.ok(output.includes('24.0 -72.0'));
});
test('la boucle complète présente un seul programme et sa sortie réellement capturée',async()=>{
  const course=(await readCourses()).find(course=>course.themeId==='pytorch');
  const chapter=course.chapters.find(ch=>ch.id==='boucle-entrainement-complete');
  assert.ok(chapter);
  const programs=chapter.blocks.filter(block=>block.code?.includes('DataLoader')&&block.code.includes('Adam'));
  assert.equal(programs.length,1);
  const code=programs[0].code;
  for(const symbol of ['manual_seed','collate_fn','CrossEntropyLoss','no_grad','torch.save','torch.load'])assert.ok(code.includes(symbol),symbol);
  const report=JSON.parse(await readFile(new URL('../scripts/verify/pytorch-additions-results.json',import.meta.url),'utf8'));
  assert.ok(report.examples['boucle-entrainement-complete'].stdout.includes('Rechargement identique : True'));
});
