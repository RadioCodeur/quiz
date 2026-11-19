import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {chromium} from '@playwright/test';
const base='https://radiocodeur.github.io/quiz/';
const revision=process.argv[2];
assert.match(revision??'',/^[a-f0-9]{40}$/);
const modules=['python-scientifique','audio-signal','pytorch','audio-ml','generation-controle','evaluation-recherche','contexte-recherche','entretien'];
const report={revision,base,workflowRun:process.argv[3],modules:0,chapters:0,notebooks:0,notebookRedirects:0,glossaryTerms:0,browserPages:[],errors:[]};
const read=path=>readFile(path,'utf8').then(JSON.parse);
const localCourses=await Promise.all(modules.map(module=>read(`public/courses/${module}.json`)));
const pytorch=localCourses.find(course=>course.themeId==='pytorch');
async function remote(path){
  const response=await fetch(base+path+'?revision='+revision,{cache:'no-store'});
  assert.equal(response.status,200,path);return response.json();
}
for(const module of modules){
  const path=`courses/${module}.json`,data=await remote(path);
  assert.deepEqual(data,await read('public/'+path),path);
  report.modules++;report.chapters+=data.chapters.length;
  if(module==='pytorch'){
    for(const chapter of data.chapters){
      assert.deepEqual(await remote(chapter.notebook),await read('public/'+chapter.notebook),chapter.notebook);
      report.notebooks++;
    }
    for(const alias of Object.keys(data.notebookAliases??{})){
      assert.deepEqual(await remote(alias),await read('public/'+alias),alias);
      report.notebookRedirects++;
    }
  }
}
assert.equal(report.chapters,localCourses.reduce((sum,course)=>sum+course.chapters.length,0));
assert.equal(report.notebooks,pytorch.chapters.length);assert.equal(report.notebookRedirects,Object.keys(pytorch.notebookAliases??{}).length);
const glossary=await remote('glossary.json');
assert.deepEqual(glossary,await read('public/glossary.json'));report.glossaryTerms=glossary.terms.length;
let browser;
try{
  browser=await chromium.launch({channel:'msedge',headless:true});
  const page=await browser.newPage({viewport:{width:360,height:800}}),failed=[];
  page.on('pageerror',error=>report.errors.push(error.message));
  page.on('response',response=>{if(response.status()>=400)failed.push(response.url());});
  await page.goto(base+'?revision='+revision);await page.locator('#start').waitFor();
  assert.equal(await page.locator('#available-count').innerText(),'200');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  report.browserPages.push('quiz');
  await page.locator('.header-nav a[href="./cours.html"]').click();await page.locator('.course-card').first().waitFor();
  assert.equal(await page.locator('.course-card').count(),8);report.browserPages.push('course-overview');
  await page.goto(base+'cours.html?theme=pytorch#tenseur-forme-type-device');await page.locator('.story-fragment').first().waitFor();
  assert.equal(await page.locator('.sidebar-title progress').getAttribute('max'),'14');
  assert.equal(await page.locator('.worked-example').first().evaluate(el=>el.closest('details').open),false);
  assert.equal(await page.locator('.chapter-toc nav a').count(),14);assert.equal(await page.locator('.reference-toc nav a').count(),8);
  report.browserPages.push('pytorch-main-path-and-references');
  await page.goto(base+'cours.html?theme=pytorch#du-pipeline-au-modele');await page.locator('.tensor-lab').waitFor();
  await page.locator('[data-lab-control="axis"]').selectOption('0');
  assert.ok((await page.locator('.lab-output').innerText()).includes('[1, 0]'));
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  report.browserPages.push('interactive-axes');
  await page.goto(base+'cours.html?theme=entretien#oral-autograd');await page.locator('.oral-model').waitFor();
  assert.equal(await page.locator('.oral-model').evaluate(el=>el.open),false);
  assert.equal(await page.locator('.oral-scaffold details').count(),3);
  await page.locator('.oral-scaffold summary').first().click();
  assert.equal(await page.locator('.oral-model').evaluate(el=>el.open),false);report.browserPages.push('oral-hints');
  await page.locator('.header-nav a[href="./glossaire.html"]').click();await page.locator('.glossary-term').first().waitFor();
  assert.equal(await page.locator('.glossary-term').count(),160);
  await page.locator('#term-search').fill('backpropagation');assert.equal(await page.locator('.glossary-term').count(),1);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);report.browserPages.push('glossary');
  assert.deepEqual(failed,[]);assert.deepEqual(report.errors,[]);
}finally{await browser?.close();}
await writeFile('test-results/audit-public-verification.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
