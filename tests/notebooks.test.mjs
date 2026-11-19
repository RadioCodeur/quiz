import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {readCourses} from '../scripts/validate-courses.mjs';
import {notebookLinks} from '../src/course-model.js';
const source=cell=>Array.isArray(cell.source)?cell.source.join(''):cell.source;
const sorted=value=>Array.isArray(value)?value.map(sorted):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(key=>[key,sorted(value[key])])):value;

test('un notebook vérifié et deux exercices accompagnent chaque chapitre PyTorch',async()=>{
  const course=(await readCourses()).find(course=>course.themeId==='pytorch');
  const files=await readdir(new URL('../public/notebooks/',import.meta.url));
  const report=JSON.parse(await readFile(new URL('../scripts/verify/notebooks-results.json',import.meta.url),'utf8'));
  const aliases=course.notebookAliases??{};
  assert.equal(course.chapters.length,22,'Le module possède 14 étapes et huit références');
  assert.equal(Object.keys(aliases).length,10,'Les anciennes adresses restent disponibles');
  assert.deepEqual(new Set(files.filter(file=>file.endsWith('.ipynb'))),new Set([...course.chapters.map(ch=>`${ch.id}.ipynb`),...Object.keys(aliases).map(path=>path.split('/').at(-1))]));
  assert.equal(report.notebooks.length,course.chapters.length);
  for(const chapter of course.chapters){
    assert.equal(chapter.notebook,`notebooks/${chapter.id}.ipynb`);
    const notebook=JSON.parse(await readFile(new URL(`../public/${chapter.notebook}`,import.meta.url),'utf8'));
    assert.equal(notebook.nbformat,4);assert.equal(notebook.nbformat_minor,5);
    assert.equal(new Set(notebook.cells.map(cell=>cell.id)).size,notebook.cells.length);
    const exercises=notebook.cells.map((cell,index)=>({cell,index})).filter(({cell})=>cell.metadata.tags?.includes('exercise'));
    assert.equal(exercises.length,2,chapter.id);
    assert.ok(exercises.every(({cell})=>cell.cell_type==='code'));
    assert.ok(notebook.cells.some(cell=>cell.metadata.tags?.includes('hint')));
    assert.equal(notebook.metadata.quiz.exerciseSolutions.length,2);
    const lastExercise=exercises.at(-1).index;
    assert.ok(notebook.cells.slice(lastExercise+1).map(source).join('\n').match(/<details>/g)?.length>=2);
    for(const cell of notebook.cells.filter(cell=>cell.cell_type==='code')){
      assert.ok(Number.isInteger(cell.execution_count),`Cellule non exécutée : ${chapter.id}`);
      assert.ok(cell.outputs.every(output=>output.output_type!=='error'));
    }
    const programs=notebook.metadata.quiz.programs;
    const companions=chapter.blocks.map((block,index)=>({block,index})).filter(({block})=>block.readingCompanion);
    assert.equal(programs.length,companions.length,'Les fragments de lecture ne sont pas des démonstrations autonomes');
    for(const {index,block} of companions){
      const program=programs.find(item=>item.blockIndex===index&&item.programId===block.programId);
      assert.ok(program,`Programme manquant : ${chapter.id}/${index}`);
      const cells=program.cellIds.map(id=>notebook.cells.find(cell=>cell.id===id));
      assert.ok(cells.every(cell=>cell?.cell_type==='code'));
      assert.ok(cells.every(cell=>cell.metadata.programId===block.programId));
      assert.equal(cells.map(source).join(''),block.code,`Programme modifié entre cellules : ${chapter.id}/${index}`);
      assert.equal(createHash('sha256').update(block.code).digest('hex'),program.sourceSha256);
      const numericalCheck=notebook.cells.find(cell=>cell.id===program.assertionCellId);
      assert.ok(numericalCheck?.metadata.tags.includes('demonstration-check'));
      assert.ok(program.assertions.length>=2);
    }
    const proof=report.notebooks.find(item=>item.path===`public/${chapter.notebook}`);
    assert.ok(proof&&proof.device==='cpu'&&proof.elapsedSeconds<120,chapter.id);
    assert.equal(proof.exerciseSolutions,2);
    assert.equal(proof.programsVerified,programs.length);
    assert.deepEqual(proof.programIds,programs.map(program=>program.programId));
    assert.equal(proof.numericalAssertions,programs.reduce((sum,program)=>sum+program.assertions.length,0));
    assert.equal(proof.exerciseDefaultOutputs.length,2);
    assert.ok(proof.exerciseDefaultOutputs.every(output=>output.includes('À compléter')&&!output.includes('Contrôle réussi')));
    assert.equal(proof.solutionOutputs.length,2);
    assert.ok(proof.solutionOutputs.every(outputs=>outputs.join('').includes('Contrôle réussi')));
    assert.equal(createHash('sha256').update(JSON.stringify(sorted(notebook))).digest('hex'),proof.notebookSha256,`Notebook modifié après exécution : ${chapter.id}`);
  }
});

test('les dix anciens notebooks deviennent des renvois Markdown vers un fichier canonique',async()=>{
  const course=(await readCourses()).find(course=>course.themeId==='pytorch');
  const canonical=new Set(course.chapters.map(chapter=>chapter.notebook));
  const report=JSON.parse(await readFile(new URL('../scripts/verify/notebooks-results.json',import.meta.url),'utf8'));
  assert.equal(report.aliases.length,Object.keys(course.notebookAliases).length);
  for(const [previous,target]of Object.entries(course.notebookAliases)){
    assert.ok(canonical.has(target)&&!canonical.has(previous));
    const bytes=await readFile(new URL(`../public/${previous}`,import.meta.url));
    const notebook=JSON.parse(bytes.toString('utf8'));
    assert.equal(notebook.metadata.quiz.notebookAlias,target);
    assert.ok(notebook.cells.length&&notebook.cells.every(cell=>cell.cell_type==='markdown'));
    assert.ok(notebook.cells.map(source).join('\n').includes(target));
    const proof=report.aliases.find(item=>item.path===`public/${previous}`);
    assert.ok(proof);
    assert.equal(proof.target,`public/${target}`);
    assert.equal(proof.codeCells,0);
    assert.equal(proof.hashFormat,'canonical-json');
    assert.equal(createHash('sha256').update(JSON.stringify(sorted(notebook))).digest('hex'),proof.sha256);
    const windows=JSON.parse(bytes.toString('utf8').replace(/\r?\n/g,'\r\n'));
    assert.equal(createHash('sha256').update(JSON.stringify(sorted(windows))).digest('hex'),proof.sha256,'Le contenu reste vérifié après un checkout avec des fins de ligne Windows');
    assert.ok(!report.notebooks.some(item=>item.path===`public/${previous}`),'Le renvoi ne possède pas de fausse preuve d’exécution');
  }
});
test('les liens Colab et téléchargement gardent le dépôt et le sous-chemin attendus',()=>{
  const links=notebookLinks('notebooks/retropropagation-a-la-main.ipynb','/quiz/');
  assert.equal(links.download,'/quiz/notebooks/retropropagation-a-la-main.ipynb');
  assert.equal(links.colab,'https://colab.research.google.com/github/RadioCodeur/quiz/blob/main/public/notebooks/retropropagation-a-la-main.ipynb');
  assert.throws(()=>notebookLinks('../secret.ipynb'));
});
