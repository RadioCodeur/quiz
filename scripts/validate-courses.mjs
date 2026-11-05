import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { readBank } from './read-bank.mjs';
import { COURSE_ORDER, wordCount } from '../src/course-model.js';
import { FIGURE_KINDS } from '../src/course-figures.js';

export async function readCourses() {
  return Promise.all(COURSE_ORDER.map(async id => JSON.parse(await readFile(new URL(`../public/courses/${id}.json`,import.meta.url),'utf8'))));
}

export function validateCourses(courses, { bank, themes, sources }) {
  const themeIds=new Set(themes.map(t=>t.id));
  const refs=new Set(sources.map(s=>s.id));
  assert.equal(courses.length,6);
  assert.deepEqual(new Set(courses.map(c=>c.themeId)),themeIds);
  const ids=new Map(bank.map(q=>[q.id,q]));
  const coverage=new Map();
  let chapters=0, words=0, figures=0, examples=0, code=0;
  for(const course of courses) {
    const check=(condition,message)=>assert.ok(condition,`${course.themeId}: ${message}`);
    check(course.title?.trim()&&course.subtitle?.trim(),'titre et sous-titre');
    check(Array.isArray(course.intro)&&course.intro.length>=2&&course.intro.every(p=>typeof p==='string'&&p.trim()),'introduction complète');
    check(Array.isArray(course.objectives)&&course.objectives.length>=3,'objectifs explicites');
    check(Array.isArray(course.prerequisites)&&course.prerequisites.every(id=>themeIds.has(id)&&id!==course.themeId),'prérequis valides');
    check(Array.isArray(course.chapters)&&course.chapters.length>=6,'au moins six chapitres');
    check(new Set(course.chapters.map(ch=>ch.id)).size===course.chapters.length,'IDs de chapitres uniques');
    for(const ch of course.chapters) {
      chapters++;
      const fail=message=>`${course.themeId}/${ch.id}: ${message}`;
      assert.match(ch.id,/^[a-z0-9]+(?:-[a-z0-9]+)*$/,fail('ID stable'));
      assert.ok(ch.title?.trim()&&ch.summary?.trim(),fail('titre et idée directrice'));
      assert.ok(Array.isArray(ch.questionIds)&&ch.questionIds.length,fail('questions reliées'));
      for(const id of ch.questionIds) {
        assert.equal(ids.get(id)?.primaryTheme,course.themeId,fail(`question principale ${id}`));
        assert.ok(!coverage.has(id),fail(`couverture unique de ${id}`));
        coverage.set(id,`${course.themeId}/${ch.id}`);
      }
      assert.ok(ch.blocks.length>=4,fail('développement explicatif'));
      let chapterWords=0;
      for(const block of ch.blocks) {
        assert.ok(['paragraph','heading','list','code','callout','example','figure'].includes(block.type),fail('type de bloc'));
        if(['paragraph','heading','callout','example'].includes(block.type))assert.ok(typeof block.text==='string'&&block.text.trim(),fail('texte non vide'));
        if(block.type==='code'){assert.ok(block.code?.trim()&&block.caption?.trim(),fail('code commenté'));code++;}
        if(block.type==='list')assert.ok(Array.isArray(block.items)&&block.items.length&&block.items.every(x=>typeof x==='string'&&x.trim()),fail('liste lisible'));
        if(block.type==='callout')assert.ok(['tip','pitfall','analogy'].includes(block.tone)&&block.label?.trim(),fail('encadré nommé'));
        if(block.type==='figure'){assert.ok(FIGURE_KINDS.includes(block.kind)&&block.caption?.trim(),fail('figure légendée'));figures++;}
        if(block.type==='example'){assert.ok(block.title?.trim(),fail('exemple titré'));examples++;}
        chapterWords+=wordCount([block.text,block.title,block.caption,...(block.items??[])].filter(Boolean).join(' '));
      }
      assert.ok(chapterWords>=220,fail(`chapitre développé (${chapterWords} mots hors code)`));
      words+=chapterWords;
      assert.ok(Array.isArray(ch.takeaways)&&ch.takeaways.length===3&&ch.takeaways.every(x=>typeof x==='string'&&x.trim()),fail('trois idées à retenir'));
      assert.ok(Array.isArray(ch.sourceIds)&&ch.sourceIds.length&&ch.sourceIds.every(id=>refs.has(id)),fail('références existantes'));
    }
  }
  assert.equal(coverage.size,bank.length,'Chaque question a un passage dans les cours');
  for(const q of bank)assert.ok(coverage.has(q.id),`Notion absente : ${q.id}`);
  // The suggested course order must put each prerequisite before its dependent course.
  for(const c of courses)for(const pre of c.prerequisites)assert.ok(COURSE_ORDER.indexOf(pre)<COURSE_ORDER.indexOf(c.themeId),`Ordre du prérequis ${pre} → ${c.themeId}`);
  assert.ok(figures>=6,'Les cours incluent des schémas');
  assert.ok(examples>=12,'Les cours incluent des exemples concrets');
  return { courses:courses.length, chapters, coveredQuestions:coverage.size, wordsExcludingCode:words, figures, examples, codeExamples:code };
}

if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)console.log(JSON.stringify(validateCourses(await readCourses(),await readBank()),null,2));
