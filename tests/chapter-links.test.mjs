import test from 'node:test';
import assert from 'node:assert/strict';
import {renderLessonList} from '../src/learning-blocks.js';

test('les liens techniques conservent le sous-répertoire Pages et échappent le texte',()=>{
  const html=renderLessonList({title:'Approfondir',items:['Une piste < concrète'],links:[{text:'Le modèle < et ses formes',themeId:'pytorch',chapterId:'boucle-entrainement-complete'}]});
  assert.ok(html.includes('./cours.html?theme=pytorch#boucle-entrainement-complete'));
  assert.ok(html.includes('Le modèle &lt; et ses formes'));
  assert.ok(!html.includes('Le modèle < et ses formes'));
});
