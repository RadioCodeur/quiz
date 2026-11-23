import assert from 'node:assert/strict';
import {chromium} from '@playwright/test';
import {spawn} from 'node:child_process';
import {mkdir,writeFile} from 'node:fs/promises';
import {STORAGE_KEY} from '../src/storage.js';
import {readBank} from './read-bank.mjs';
import {fileURLToPath} from 'node:url';

process.chdir(fileURLToPath(new URL('../',import.meta.url)));
const remote=process.argv[2],base=remote??'http://127.0.0.1:4190/';
const server=remote?null:spawn(process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','4190','--strictPort'],{stdio:'pipe',windowsHide:true});
const checks=[],errors=[],contrasts=[];
const key='a-lecoute.theme.v1';
let browser;
const check=async(name,fn)=>{await fn();checks.push(name);console.log('✓ '+name);};
async function contrast(page,selectors){
  await page.waitForTimeout(180); // Let existing card background transitions settle.
  const readings=await page.evaluate(selectors=>{
    const rgba=value=>{const values=value.match(/[\d.]+/g)?.map(Number)??[0,0,0,0];return [...values.slice(0,3),values[3]??1];};
    const blend=(front,back)=>front.slice(0,3).map((v,i)=>v*front[3]+back[i]*(1-front[3]));
    const lum=rgb=>rgb.map(value=>{const v=value/255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((n,value,i)=>n+value*[.2126,.7152,.0722][i],0);
    return selectors.flatMap(selector=>[...document.querySelectorAll(selector)].filter(el=>el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden').slice(0,3).map(el=>{
      const ancestors=[];for(let p=el;p;p=p.parentElement)ancestors.unshift(p);
      let bg=[255,255,255];for(const p of ancestors)bg=blend(rgba(getComputedStyle(p).backgroundColor),bg);
      const fg=blend(rgba(getComputedStyle(el).color),bg),a=lum(fg),b=lum(bg);
      return {selector,text:el.textContent.trim().slice(0,50),ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
    }));
  },selectors);
  contrasts.push(...readings);
  for(const reading of readings)assert.ok(reading.ratio>=4.5,`Contraste ${reading.ratio.toFixed(2)} : ${reading.selector} (${reading.text})`);
}
try{
  if(server)for(let i=0;i<80;i++){try{if((await fetch(base)).ok)break;}catch{}await new Promise(resolve=>setTimeout(resolve,125));}
  await mkdir('test-results',{recursive:true});
  browser=await chromium.launch({channel:'msedge',headless:true});
  const context=await browser.newContext({colorScheme:'light',viewport:{width:1440,height:1050}}),page=await context.newPage();
  page.on('pageerror',error=>errors.push(error.message));
  await check('préférence système initiale et bouton utilisable au clavier',async()=>{
    await page.goto(base);await page.locator('#start').waitFor();
    assert.equal(await page.locator('html').getAttribute('data-theme'),'light');
    await page.locator('[data-theme-toggle]').focus();await page.keyboard.press('Space');
    assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
    assert.equal(await page.locator('[data-theme-toggle]').getAttribute('aria-pressed'),'true');
    assert.equal(await page.evaluate(key=>localStorage.getItem(key),key),'dark');
    await contrast(page,['.theme-description','.theme-count','.session-card .field-label','.session-card .available','.theme-toggle']);
    await page.screenshot({path:`test-results/theme-${remote?'public':'local'}-quiz.png`});
  });
  await check('thème conservé au rechargement sans modifier la session de quiz',async()=>{
    const {bank}=await readBank();
    await page.locator('#question-count').selectOption('10');await page.locator('#start').click();
    const session=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).session,STORAGE_KEY);
    const question=bank.find(q=>q.id===session.questionIds[session.index]),wrong=question.options.find(option=>option.id!==question.correctOptionId);
    await page.locator(`[data-option="${wrong.id}"]`).click();
    await contrast(page,['.answer.correct','.answer.wrong','.feedback p','.answer-letter']);
    const before=await page.evaluate(key=>localStorage.getItem(key),STORAGE_KEY);
    await page.locator('[data-theme-toggle]').click();await page.locator('[data-theme-toggle]').click();
    assert.equal(await page.evaluate(key=>localStorage.getItem(key),STORAGE_KEY),before);
    await page.reload();await page.locator('#next').waitFor();
    assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
    assert.equal(await page.evaluate(key=>localStorage.getItem(key),STORAGE_KEY),before);
  });
  await check('cours, code, tableaux, feedback et glossaire en sombre',async()=>{
    await page.goto(base+'cours.html?theme=pytorch#du-pipeline-au-modele');await page.locator('#lesson-title').waitFor();
    assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
    await contrast(page,['.lesson-summary','.lesson-body>p','.story-fragment code','.fragment-context','.lab-output td','.lab-output th','.lesson-level','.toc-reading-group>p']);
    await page.locator('[data-checkpoint-option]').first().click();
    await contrast(page,['.checkpoint-options .is-wrong','.checkpoint-options .is-correct','.specific-feedback']);
    await page.screenshot({path:`test-results/theme-${remote?'public':'local'}-course.png`});
    await page.goto(base+'cours.html?theme=audio-signal#amplitude-puissance-decibels');await page.locator('[data-audio-lab]').waitFor();
    await contrast(page,['.lab-clip header p','.lab-transform','.lab-listening-note','.lab-controls label','.media-credit']);
    await page.goto(base+'glossaire.html');await page.locator('.glossary-term').first().waitFor();
    await contrast(page,['.glossary-search label','.glossary-term dt','.glossary-term dd','.glossary-term small']);
    await page.locator('[data-theme-toggle]').click();await page.reload();await page.locator('.glossary-term').first().waitFor();
    assert.equal(await page.locator('html').getAttribute('data-theme'),'light');
  });
  await check('système sombre respecté et choix manuel prioritaire',async()=>{
    const ctx=await browser.newContext({colorScheme:'dark'}),p=await ctx.newPage();
    await p.goto(base);await p.locator('#start').waitFor();
    assert.equal(await p.locator('html').getAttribute('data-theme'),'dark');
    await p.emulateMedia({colorScheme:'light'});await p.waitForFunction(()=>document.documentElement.dataset.theme==='light');
    await p.locator('[data-theme-toggle]').click();
    await p.emulateMedia({colorScheme:'dark'});await p.emulateMedia({colorScheme:'light'});
    assert.equal(await p.locator('html').getAttribute('data-theme'),'dark');
    await ctx.close();
  });
  await check('stockage bloqué : bascule conservée en mémoire sans erreur',async()=>{
    const ctx=await browser.newContext({colorScheme:'light'});
    await ctx.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Blocked','SecurityError');}}));
    const p=await ctx.newPage();p.on('pageerror',error=>errors.push(error.message));
    await p.goto(base);await p.locator('#start').waitFor();
    await p.locator('[data-theme-toggle]').click();assert.equal(await p.locator('html').getAttribute('data-theme'),'dark');
    await p.locator('[data-theme-toggle]').click();assert.equal(await p.locator('html').getAttribute('data-theme'),'light');
    await ctx.close();
  });
  await check('navigation sans débordement à 320, 360, 530 et 600 px',async()=>{
    await page.locator('[data-theme-toggle]').click();
    for(const width of [320,360,530,600]){
      await page.setViewportSize({width,height:800});
      for(const path of ['','cours.html?theme=pytorch#padding-et-collate','glossaire.html']){
        await page.goto(base+path);await page.locator('[data-theme-toggle]').waitFor();
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${width} ${path}`);
        const button=await page.locator('[data-theme-toggle]').boundingBox();assert.ok(button.width>=44&&button.height>=44);
      }
    }
    await page.setViewportSize({width:360,height:800});await page.screenshot({path:`test-results/theme-${remote?'public':'local'}-mobile.png`});
  });
  assert.deepEqual(errors,[]);
  const report={base,browser:browser.version(),checks,contrastSamples:contrasts.length,minimumContrast:Math.min(...contrasts.map(item=>item.ratio)),errors};
  await writeFile(`test-results/theme-${remote?'public':'local'}.json`,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
}finally{await browser?.close();server?.kill();}
