import { chromium } from '@playwright/test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFile, mkdir } from 'node:fs/promises';
import { readBank } from './read-bank.mjs';
import { STORAGE_KEY } from '../src/storage.js';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

process.chdir(fileURLToPath(new URL('../', import.meta.url)));
const { bank } = await readBank();
const byId = new Map(bank.map(q => [q.id,q]));
const base = 'http://127.0.0.1:4188';
const vite = spawn(process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','4188','--strictPort'],{stdio:'pipe',windowsHide:true});
let browser, staticServer;
const checks = [];
const check = async (name, fn) => { await fn(); checks.push(name); console.log(`✓ ${name}`); };
async function waitForServer(url) {
  for (let i=0;i<80;i++) {
    try { if ((await fetch(url)).ok) return; } catch {}
    await new Promise(resolve=>setTimeout(resolve,125));
  }
  throw new Error(`Serveur indisponible : ${url}`);
}
try {
  await mkdir('test-results',{recursive:true});
  await waitForServer(base);
  try { browser = await chromium.launch({channel:'msedge',headless:true}); console.log(`Microsoft Edge ${browser.version()}`); }
  catch { browser = await chromium.launch({headless:true}); console.log(`Chromium ${browser.version()}`); }
  const page = await browser.newPage({viewport:{width:1440,height:1100}});
  const errors = [];
  page.on('pageerror',error => errors.push(error.message));
  await page.goto(base);
  await page.locator('#start').waitFor();
  const getSession = () => page.evaluate(key=>JSON.parse(localStorage.getItem(key)).session,STORAGE_KEY);
  const clickAnswer = async correct => {
    const session = await getSession();
    const q = byId.get(session.questionIds[session.index]);
    const id = correct ? q.correctOptionId : q.options.find(o=>o.id!==q.correctOptionId).id;
    await page.locator(`[data-option="${id}"]`).click();
    return q;
  };
  await check('configuration : 200 questions, 50 par défaut, aucun thème bloque le départ',async()=>{
    assert.equal(await page.locator('#available-count').innerText(),'200');
    assert.equal(await page.locator('#question-count').inputValue(),'50');
    await page.screenshot({path:'test-results/desktop-configuration.png',fullPage:true});
    await page.locator('#all-themes').uncheck();
    assert.equal(await page.locator('#start').isDisabled(),true);
    await page.locator('[name=theme][value=pytorch]').check();
    await page.locator('[name=theme][value=audio-ml]').check();
    const expected = bank.filter(q=>q.themes.includes('pytorch')||q.themes.includes('audio-ml')).length;
    assert.equal(await page.locator('#available-count').innerText(),String(expected));
    await page.locator('#all-themes').check();
    await page.locator('#question-count').selectOption('10');
  });
  await check('réponse correcte, verrouillage et reprise exacte après rafraîchissement',async()=>{
    await page.locator('#start').click();
    await clickAnswer(true);
    assert.equal(await page.locator('.answer:disabled').count(),4);
    assert.equal(await page.locator('.feedback').count(),1);
    assert.equal(await page.locator('.answer.correct .answer-state').innerText(),'✓ Bonne réponse');
    const snapshot = await getSession();
    await page.reload(); await page.locator('#next').waitFor();
    assert.deepEqual(await getSession(),snapshot);
    await page.locator('#next').click();
  });
  let wrongQuestion;
  await check('erreur : choix personnel, bonne réponse et explication toujours visibles',async()=>{
    wrongQuestion = await clickAnswer(false);
    assert.equal(await page.locator('.answer.wrong').count(),1);
    assert.equal(await page.locator('.answer.correct').count(),1);
    assert.ok((await page.locator('.feedback').innerText()).includes(wrongQuestion.explanation));
    await page.screenshot({path:'test-results/desktop-correction.png',fullPage:true});
    await page.locator('#next').click();
  });
  await check('fin de session : bilan 9/10, erreurs consultables et score conservé',async()=>{
    for(let i=2;i<10;i++) { await clickAnswer(true); await page.locator('#next').click(); }
    assert.ok((await page.locator('.score-card').innerText()).includes('9 bonnes réponses sur 10'));
    assert.equal(await page.locator('.error-item').count(),1);
    await page.locator('.error-item>summary').click();
    assert.ok((await page.locator('.error-body').innerText()).includes(wrongQuestion.explanation));
    await page.screenshot({path:'test-results/desktop-bilan.png',fullPage:true});
    await page.reload(); await page.locator('#retry').waitFor();
    assert.equal((await getSession()).completed,true);
  });
  await check('refaire une seule erreur, puis session parfaite et nouvelle configuration',async()=>{
    await page.locator('#retry').click();
    const s=await getSession();
    assert.deepEqual(s.questionIds,[wrongQuestion.id]);
    assert.equal(s.mode,'errors');
    await clickAnswer(true); await page.locator('#next').click();
    assert.equal(await page.locator('#retry').isDisabled(),true);
    await page.locator('#new-session').click();
    assert.equal(await page.locator('#start').count(),1);
    assert.equal(await page.evaluate(key=>localStorage.getItem(key),STORAGE_KEY),null);
  });
  await check('abandon : annulation puis confirmation',async()=>{
    await page.locator('#start').click();
    page.once('dialog',d=>d.dismiss()); await page.locator('#abandon').click();
    assert.equal(await page.locator('.question-card').count(),1);
    page.once('dialog',d=>d.accept()); await page.locator('#abandon').click();
    assert.equal(await page.locator('#start').count(),1);
  });
  await check('sauvegarde corrompue et banque modifiée gérées sans erreur',async()=>{
    await page.evaluate(key=>localStorage.setItem(key,'broken JSON'),STORAGE_KEY);
    await page.reload(); await page.locator('#start').waitFor();
    assert.ok((await page.locator('.notice').innerText()).includes('invalide'));
    await page.locator('#start').click();
    await page.evaluate(key=>{const s=JSON.parse(localStorage.getItem(key));s.signature='obsolete';localStorage.setItem(key,JSON.stringify(s));},STORAGE_KEY);
    await page.reload(); await page.locator('#start').waitFor();
    assert.ok((await page.locator('.notice').innerText()).includes('banque a changé'));
  });
  await check('mobile 360 px : configuration et code sans débordement horizontal',async()=>{
    await page.setViewportSize({width:360,height:800});
    await page.evaluate(()=>localStorage.clear()); await page.reload(); await page.locator('#start').waitFor();
    await page.screenshot({path:'test-results/mobile-configuration.png',fullPage:true});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    const s={version:1,mode:'errors',questionIds:[bank.find(q=>q.code && q.code.length>120).id],optionOrders:{},answers:{},index:0,completed:false,startedAt:new Date().toISOString()};
    s.optionOrders[s.questionIds[0]]=byId.get(s.questionIds[0]).options.map(o=>o.id);
    await page.locator('#start').click();
    await page.evaluate(({key,s})=>{const old=JSON.parse(localStorage.getItem(key));old.session=s;localStorage.setItem(key,JSON.stringify(old));},{key:STORAGE_KEY,s});
    await page.reload(); await page.locator('.question-card').waitFor();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:'test-results/mobile-question.png',fullPage:true});
    await clickAnswer(false);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:'test-results/mobile-correction.png',fullPage:true});
    await page.locator('#next').click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:'test-results/mobile-bilan.png',fullPage:true});
  });
  await check('stockage indisponible : session complète utilisable en mémoire',async()=>{
    const isolated=await browser.newContext({viewport:{width:390,height:844}});
    await isolated.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Blocked','SecurityError');}}));
    const p=await isolated.newPage(); await p.goto(base); await p.locator('#start').waitFor();
    assert.ok((await p.locator('.notice').innerText()).includes('indisponible'));
    await p.locator('#question-count').selectOption('10'); await p.locator('#start').click();
    for(let i=0;i<10;i++){await p.locator('.answer').first().click();await p.locator('#next').click();}
    assert.equal(await p.locator('.score-card').count(),1);
    await isolated.close();
  });
  await check('clavier : focus visible et sélection par Espace',async()=>{
    await page.evaluate(()=>localStorage.clear()); await page.reload(); await page.locator('#start').waitFor();
    await page.locator('#all-themes').focus(); await page.keyboard.press('Space');
    assert.equal(await page.locator('#start').isDisabled(),true);
    await page.keyboard.press('Space');
    await page.locator('#question-count').selectOption('10');
    await page.locator('#start').focus(); await page.keyboard.press('Enter');
    await page.locator('.answer').first().focus(); await page.keyboard.press('Enter');
    assert.equal(await page.locator('.feedback').count(),1);
    assert.equal(await page.locator('.feedback').evaluate(el=>el===document.activeElement),true);
  });
  await check('construction servie sous /qr-entretien/ : JSON, assets et quiz fonctionnels',async()=>{
    const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'};
    staticServer=createServer(async(req,res)=>{
      try{
        const url=new URL(req.url,'http://localhost');
        if(!url.pathname.startsWith('/qr-entretien/')) {res.writeHead(404).end();return;}
        const relative=decodeURIComponent(url.pathname.slice('/qr-entretien/'.length))||'index.html';
        const file=path.resolve('dist',relative);
        if(!file.startsWith(path.resolve('dist')+path.sep)) {res.writeHead(403).end();return;}
        res.setHeader('Content-Type',types[path.extname(file)]??'application/octet-stream');
        res.end(await readFile(file));
      }catch{res.writeHead(404).end();}
    });
    await new Promise(resolve=>staticServer.listen(4189,'127.0.0.1',resolve));
    const p=await browser.newPage();
    const failed=[];p.on('response',r=>{if(r.status()>=400)failed.push(r.url());});
    await p.goto('http://127.0.0.1:4189/qr-entretien/');await p.locator('#start').waitFor();
    assert.equal(await p.locator('#available-count').innerText(),'200');
    await p.locator('#start').click();await p.locator('.answer').first().click();
    assert.equal(await p.locator('.feedback').count(),1);
    assert.deepEqual(failed,[]);await p.close();
  });
  assert.deepEqual(errors,[],'Aucune exception navigateur');
  console.log(`${checks.length} contrôles navigateur réussis.`);
} finally {
  await browser?.close();
  vite.kill();
  if(staticServer) await new Promise(resolve=>staticServer.close(resolve));
}
