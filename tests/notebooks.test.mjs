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
  assert.equal(files.filter(file=>file.endsWith('.ipynb')).length,course.chapters.length);
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
    for(const [index,block] of chapter.blocks.entries())if(block.code&&(block.language??'python')==='python'){
      const program=programs.find(item=>item.blockIndex===index);
      assert.ok(program,`Programme manquant : ${chapter.id}/${index}`);
      const cells=program.cellIds.map(id=>notebook.cells.find(cell=>cell.id===id));
      assert.ok(cells.every(cell=>cell?.cell_type==='code'));
      assert.equal(cells.map(source).join(''),block.code,`Programme modifié entre cellules : ${chapter.id}/${index}`);
    }
    const proof=report.notebooks.find(item=>item.path===`public/${chapter.notebook}`);
    assert.ok(proof&&proof.device==='cpu'&&proof.elapsedSeconds<120,chapter.id);
    assert.equal(proof.exerciseSolutions,2);
    assert.equal(createHash('sha256').update(JSON.stringify(sorted(notebook))).digest('hex'),proof.notebookSha256,`Notebook modifié après exécution : ${chapter.id}`);
  }
});
test('les liens Colab et téléchargement gardent le dépôt et le sous-chemin attendus',()=>{
  const links=notebookLinks('notebooks/retropropagation-a-la-main.ipynb','/quiz/');
  assert.equal(links.download,'/quiz/notebooks/retropropagation-a-la-main.ipynb');
  assert.equal(links.colab,'https://colab.research.google.com/github/RadioCodeur/quiz/blob/main/public/notebooks/retropropagation-a-la-main.ipynb');
  assert.throws(()=>notebookLinks('../secret.ipynb'));
});
