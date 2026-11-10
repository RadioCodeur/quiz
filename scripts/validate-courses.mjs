import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { readBank } from './read-bank.mjs';
import { COURSE_ORDER, wordCount, chapterText } from '../src/course-model.js';
import { FIGURE_KINDS } from '../src/course-figures.js';

export async function readCourses() {
  return Promise.all(COURSE_ORDER.map(async id => JSON.parse(await readFile(new URL(`../public/courses/${id}.json`,import.meta.url),'utf8'))));
}

export function validateCourses(courses, { bank, themes, sources }) {
  const themeIds=new Set(themes.map(t=>t.id));
  const allRefs=[...sources,...courses.flatMap(course=>course.references??[])];
  const refs=new Set(allRefs.map(s=>s.id));
  assert.equal(refs.size,allRefs.length,'Les identifiants de références restent uniques');
  for(const source of allRefs){assert.ok(source.id&&source.title&&new URL(source.url).protocol==='https:',`Référence complète : ${source.id}`);assert.match(source.accessed,/^\d{4}-\d{2}-\d{2}$/);}
  assert.equal(courses.length,6);
  assert.deepEqual(new Set(courses.map(c=>c.themeId)),themeIds);
  const ids=new Map(bank.map(q=>[q.id,q]));
  const coverage=new Map();
  let chapters=0, words=0, figures=0, examples=0, code=0, visuals=0, plots=0, walkthroughs=0, checkpoints=0;
  for(const course of courses) {
    const check=(condition,message)=>assert.ok(condition,`${course.themeId}: ${message}`);
    check(course.edition===2,'édition pédagogique 2');
    check(course.title?.trim()&&course.subtitle?.trim(),'titre et sous-titre');
    check(Array.isArray(course.intro)&&course.intro.length>=2&&course.intro.every(p=>typeof p==='string'&&p.trim()),'introduction complète');
    check(Array.isArray(course.objectives)&&course.objectives.length>=3,'objectifs explicites');
    check(Array.isArray(course.prerequisites)&&course.prerequisites.every(id=>themeIds.has(id)&&id!==course.themeId),'prérequis valides');
    check(Array.isArray(course.chapters)&&course.chapters.length>=6,'au moins six chapitres');
    check(new Set(course.chapters.map(ch=>ch.id)).size===course.chapters.length,'IDs de chapitres uniques');
    const journey=course.journey;
    check(journey&&['title','scenario','startingPoint','destination'].every(key=>typeof journey[key]==='string'&&journey[key].trim()),'projet, départ et destination');
    check(journey.scope?.length>=3&&journey.scope.every(x=>typeof x==='string'&&x.trim()),'compétences visées');
    check(journey.stages?.length>=3&&journey.stages.every(stage=>stage.title?.trim()&&stage.chapterIds.length),'étapes du parcours');
    assert.deepEqual(journey.stages.flatMap(stage=>stage.chapterIds),course.chapters.map(ch=>ch.id),`${course.themeId}: tous les chapitres dans l’ordre du parcours`);
    for(const ch of course.chapters) {
      chapters++;
      const fail=message=>`${course.themeId}/${ch.id}: ${message}`;
      assert.match(ch.id,/^[a-z0-9]+(?:-[a-z0-9]+)*$/,fail('ID stable'));
      assert.ok(ch.title?.trim()&&ch.summary?.trim(),fail('titre et idée directrice'));
      assert.ok(Array.isArray(ch.questionIds),fail('questions reliées ; vide autorisé pour un chapitre de fondations'));
      assert.ok(ch.context&&['recall','problem','why','connection','next'].every(key=>typeof ch.context[key]==='string'&&ch.context[key].trim()),fail('rappel, problème, utilité et transitions'));
      for(const id of ch.questionIds) {
        assert.equal(ids.get(id)?.primaryTheme,course.themeId,fail(`question principale ${id}`));
        assert.ok(!coverage.has(id),fail(`couverture unique de ${id}`));
        coverage.set(id,`${course.themeId}/${ch.id}`);
      }
      assert.ok(ch.blocks.length>=4,fail('développement explicatif'));
      assert.ok(ch.blocks.some(b=>b.type==='walkthrough'),fail('exemple résolu pas à pas'));
      assert.ok(ch.blocks.some(b=>['visual','plot'].includes(b.type)),fail('schéma ou graphique propre à la notion'));
      let chapterWords=0;
      for(const block of ch.blocks) {
        assert.ok(['paragraph','heading','list','code','callout','example','figure','visual','plot','walkthrough'].includes(block.type),fail('type de bloc'));
        if(['paragraph','heading','callout','example'].includes(block.type))assert.ok(typeof block.text==='string'&&block.text.trim(),fail('texte non vide'));
        if(block.type==='code'){assert.ok(block.code?.trim()&&block.caption?.trim(),fail('code commenté'));code++;}
        if(block.type==='list')assert.ok(Array.isArray(block.items)&&block.items.length&&block.items.every(x=>typeof x==='string'&&x.trim()),fail('liste lisible'));
        if(block.type==='callout')assert.ok(['tip','pitfall','analogy'].includes(block.tone)&&block.label?.trim(),fail('encadré nommé'));
        if(block.type==='figure'){assert.ok(FIGURE_KINDS.includes(block.kind)&&block.caption?.trim(),fail('figure légendée'));figures++;}
        if(block.type==='example'){assert.ok(block.title?.trim(),fail('exemple titré'));examples++;}
        if(block.type==='visual'){
          visuals++;assert.ok(block.title?.trim()&&block.caption?.trim(),fail('schéma titré et interprété'));
          assert.ok(['flow','comparison','table'].includes(block.kind),fail('type de schéma'));
          if(block.kind==='flow')assert.ok(block.nodes?.length>=2&&block.nodes.every(n=>n.title?.trim()&&n.text?.trim()),fail('flux explicite'));
          if(block.kind==='comparison')assert.ok(block.panels?.length>=2&&block.panels.every(p=>p.title?.trim()&&p.items?.length&&p.items.every(x=>typeof x==='string'&&x.trim())),fail('comparaison complète'));
          if(block.kind==='table')assert.ok(block.columns?.length>=2&&block.rows?.length&&block.rows.every(row=>row.length===block.columns.length&&row.every(cell=>String(cell).trim())),fail('tableau cohérent'));
        }
        if(block.type==='plot'){
          plots++;assert.ok(['title','xLabel','yLabel','caption'].every(key=>block[key]?.trim()),fail('graphique avec axes et interprétation'));
          assert.ok(block.series?.length&&block.series.every(s=>s.name?.trim()&&s.points.length>=2&&s.points.every((p,i)=>p.length===2&&p.every(Number.isFinite)&&(!i||p[0]>=s.points[i-1][0]))),fail('coordonnées finies et ordonnées'));
        }
        if(block.type==='walkthrough'){
          walkthroughs++;assert.ok(block.title?.trim()&&block.goal?.trim()&&block.result?.trim(),fail('objectif et conclusion de l’exemple'));
          assert.ok(block.steps.length>=3&&block.steps.length<=6,fail('trois à six étapes'));
          const lineCount=block.code?.split('\n').length??0;
          if(block.code){code++;assert.ok(block.steps.some(step=>step.lines?.length),fail('lien entre les étapes et les lignes de code'));}
          for(const step of block.steps){assert.ok(step.title?.trim()&&step.text?.trim(),fail('étape expliquée'));assert.ok(step.lines===undefined||(Array.isArray(step.lines)&&step.lines.every(n=>Number.isInteger(n)&&n>=1&&n<=lineCount)),fail('lignes de code présentes'));}
        }
        chapterWords+=wordCount([block.text,block.title,block.caption,...(block.items??[])].filter(Boolean).join(' '));
      }
      chapterWords=wordCount(chapterText(ch));
      assert.ok(chapterWords>=350,fail(`chapitre développé (${chapterWords} mots hors code)`));
      words+=chapterWords;
      assert.ok(Array.isArray(ch.takeaways)&&ch.takeaways.length===3&&ch.takeaways.every(x=>typeof x==='string'&&x.trim()),fail('trois idées à retenir'));
      assert.ok(Array.isArray(ch.sourceIds)&&ch.sourceIds.length&&ch.sourceIds.every(id=>refs.has(id)),fail('références existantes'));
      const checkpoint=ch.checkpoint;
      assert.ok(checkpoint?.prompt?.trim()&&checkpoint.explanation?.trim(),fail('QCM de transfert expliqué'));
      assert.ok(checkpoint.options?.length===4&&checkpoint.options.every(o=>o.id?.trim()&&o.text?.trim()),fail('quatre propositions'));
      assert.equal(new Set(checkpoint.options.map(o=>o.id)).size,4,fail('IDs de propositions distincts'));
      assert.equal(new Set(checkpoint.options.map(o=>o.text.trim())).size,4,fail('propositions distinctes'));
      assert.ok(checkpoint.options.some(o=>o.id===checkpoint.correctOptionId),fail('bonne réponse existante'));checkpoints++;
    }
  }
  assert.equal(coverage.size,bank.length,'Chaque question a un passage dans les cours');
  for(const q of bank)assert.ok(coverage.has(q.id),`Notion absente : ${q.id}`);
  // The suggested course order must put each prerequisite before its dependent course.
  for(const c of courses)for(const pre of c.prerequisites)assert.ok(COURSE_ORDER.indexOf(pre)<COURSE_ORDER.indexOf(c.themeId),`Ordre du prérequis ${pre} → ${c.themeId}`);
  assert.ok(visuals+plots>=chapters,'Des représentations dans chaque chapitre');
  assert.ok(plots>=9,'Graphiques numériques répartis dans les cours');
  return { courses:courses.length,chapters,coveredQuestions:coverage.size,wordsExcludingCode:words,figures,visuals,plots,examples,codeExamples:code,walkthroughs,checkpoints,references:refs.size };
}

if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)console.log(JSON.stringify(validateCourses(await readCourses(),await readBank()),null,2));
