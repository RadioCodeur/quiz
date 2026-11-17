import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {readCourses} from '../scripts/validate-courses.mjs';
import {filterTerms,normalizeTerm} from '../src/glossary-model.js';
const courses=await readCourses();
const oral=courses.find(course=>course.themeId==='entretien');
const glossary=JSON.parse(await readFile(new URL('../public/glossary.json',import.meta.url),'utf8'));

test('25 réponses orales complètes et un pitch hypothétique restent adaptés à leur durée',()=>{
  const questions=oral.chapters.filter(chapter=>chapter.oral.kind==='question');
  assert.equal(questions.length,25);
  for(const chapter of oral.chapters){
    const words=chapter.blocks.filter(block=>block.role==='oral-answer').map(block=>block.text).join(' ').split(/\s+/u).length;
    assert.equal(words,chapter.oral.answerWords);
    assert.ok(chapter.oral.kind==='pitch'?words>=260&&words<=320:words>=150&&words<=225);
    assert.equal(chapter.blocks.find(block=>block.title==='Trois points obligatoires').items.length,3);
    assert.equal(chapter.blocks.filter(block=>block.type==='callout'&&block.tone==='pitfall').length,1);
    assert.equal(chapter.blocks.filter(block=>block.title==='Relance probable du jury').length,1);
  }
  const pitch=oral.chapters.find(chapter=>chapter.oral.kind==='pitch');
  assert.ok(pitch.blocks.some(block=>block.role==='pitch-template'&&block.items.length>=5));
  assert.match(pitch.blocks.filter(block=>block.role==='oral-answer').map(block=>block.text).join(' '),/hypothétique/u);
});

test('le glossaire contient au moins 120 paires uniques et chaque définition renvoie à un chapitre',()=>{
  const {terms}=glossary;
  assert.ok(terms.length>=120);
  assert.equal(new Set(terms.map(term=>term.id)).size,terms.length);
  assert.equal(new Set(terms.map(term=>normalizeTerm(term.fr))).size,terms.length);
  assert.equal(new Set(terms.map(term=>term.category)).size,6);
  const segmenter=new Intl.Segmenter('fr',{granularity:'sentence'});
  for(const term of terms){
    assert.match(term.id,/^[a-z0-9]+(?:-[a-z0-9]+)*$/u);
    assert.ok(term.fr&&term.en&&term.definition);
    assert.ok(courses.some(course=>course.themeId===term.themeId&&course.chapters.some(chapter=>chapter.id===term.chapterId)),term.id);
    assert.ok([...segmenter.segment(term.definition)].every(part=>part.segment.trim().split(/\s+/u).length<=30),term.id);
  }
});

test('la recherche accepte les deux langues, les accents et leur combinaison avec le domaine',()=>{
  const terms=[{fr:'Rétropropagation',en:'backpropagation',definition:'Calcul des dérivées.',category:'PyTorch'},{fr:'Décibel',en:'decibel',definition:'Un rapport logarithmique.',category:'Signal audio'}];
  assert.equal(filterTerms(terms,'RETROPROPAGATION')[0].en,'backpropagation');
  assert.equal(filterTerms(terms,'backpropagation')[0].fr,'Rétropropagation');
  assert.equal(filterTerms(terms,'decibel','PyTorch').length,0);
  assert.equal(filterTerms(terms,'decibel','Signal audio').length,1);
  assert.equal(filterTerms(terms,'inconnu').length,0);
});
