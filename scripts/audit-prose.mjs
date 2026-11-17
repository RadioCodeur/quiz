import {readCourses} from './validate-courses.mjs';
import {chapterText,wordCount} from '../src/course-model.js';
import {pathToFileURL} from 'node:url';
import {writeFile} from 'node:fs/promises';

const segmenter=new Intl.Segmenter('fr',{granularity:'sentence'});
export function proseFields(chapter){
  const fields=[];
  const add=(path,value)=>{if(typeof value==='string'&&value.trim())fields.push({path,text:value});};
  add('summary',chapter.summary);
  add('lengthJustification',chapter.lengthJustification);
  for(const [key,value] of Object.entries(chapter.context??{}))add(`context.${key}`,value);
  for(const [key,value] of Object.entries(chapter.progression??{}))add(`progression.${key}`,value);
  for(const [i,notion] of (chapter.notions??[]).entries())add(`notions.${i}`,notion.explanation);
  for(const [i,b] of chapter.blocks.entries()){
    for(const key of ['text','title','caption','goal','result','introduction','explanation','conclusion'])add(`blocks.${i}.${key}`,b[key]);
    for(const key of ['items','observations','reading'])for(const [j,value] of (b[key]??[]).entries())add(`blocks.${i}.${key}.${j}`,value);
    for(const [j,step] of (b.steps??[]).entries()){add(`blocks.${i}.steps.${j}.title`,step.title);add(`blocks.${i}.steps.${j}.text`,step.text);}
    for(const [j,node] of (b.nodes??[]).entries()){add(`blocks.${i}.nodes.${j}.title`,node.title);add(`blocks.${i}.nodes.${j}.text`,node.text);}
    for(const [j,panel] of (b.panels??[]).entries()){add(`blocks.${i}.panels.${j}.title`,panel.title);for(const [k,item] of (panel.items??[]).entries())add(`blocks.${i}.panels.${j}.items.${k}`,item);}
    if(b.variant){add(`blocks.${i}.variant.change`,b.variant.change);add(`blocks.${i}.variant.explanation`,b.variant.explanation);}
  }
  for(const [i,value] of chapter.takeaways.entries())add(`takeaways.${i}`,value);
  // Existing checkpoint wording is protected by V5; code, formula states and bibliography are separate from prose.
  return fields;
}
export function auditModule(course){
  const texts=[...course.intro,...course.objectives,...['title','scenario','startingPoint','destination'].map(key=>course.journey[key]),...course.journey.scope,...course.journey.stages.map(stage=>stage.title),course.moduleIntroduction.startingPoint,course.moduleIntroduction.goal,...course.moduleIntroduction.concepts.flatMap(concept=>[concept.name,concept.explanation])];
  return texts.flatMap(text=>[...segmenter.segment(text)].map(part=>({sentence:part.segment.trim(),words:wordCount(part.segment)}))).filter(sentence=>sentence.words>30);
}
export function auditChapter(course,chapter){
  const sentences=proseFields(chapter).flatMap(field=>[...segmenter.segment(field.text)].map(part=>({...field,sentence:part.segment.trim(),words:wordCount(part.segment)})));
  const long=sentences.filter(sentence=>sentence.words>30);
  const words=wordCount(chapterText(chapter));
  const last=chapter.blocks.at(-1);
  return {themeId:course.themeId,chapterId:chapter.id,words,meanSentenceWords:Number((sentences.reduce((n,s)=>n+s.words,0)/Math.max(sentences.length,1)).toFixed(2)),longSentences:long,interviewEnding:last?.type==='paragraph'&&last.text.startsWith('À dire en entretien :'),lengthJustification:chapter.lengthJustification??null};
}
export async function auditProse(){return (await readCourses()).flatMap(course=>course.chapters.map(chapter=>auditChapter(course,chapter)));}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  const report=await auditProse(),theme=process.argv.find(value=>value.startsWith('--theme='))?.slice(8);
  const selected=theme?report.filter(chapter=>chapter.themeId===theme):report;
  await writeFile(new URL('./verify/prose-audit.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
  const failures=selected.filter(ch=>ch.longSentences.length||(ch.words>1100&&!ch.lengthJustification)||!ch.interviewEnding);
  console.log(JSON.stringify({chapters:selected.length,failures:failures.map(ch=>({id:`${ch.themeId}/${ch.chapterId}`,words:ch.words,longSentences:ch.longSentences.length,interviewEnding:ch.interviewEnding}))},null,2));
  if(process.argv.includes('--strict')&&failures.length)process.exitCode=1;
}
