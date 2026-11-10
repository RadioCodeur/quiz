import { shuffle } from './quiz.js';
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' })[char]);
const number = value => new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 3 }).format(value);

export function renderVisual(block) {
  let body;
  if (block.kind === 'flow') {
    body = `<ol class="concept-flow">${block.nodes.map((node,index) => `<li><span class="flow-index">${index+1}</span><strong>${escape(node.title)}</strong><p>${escape(node.text)}</p></li>`).join('')}</ol>`;
  } else if (block.kind === 'comparison') {
    body = `<div class="concept-comparison">${block.panels.map(panel => `<section><h4>${escape(panel.title)}</h4><ul>${panel.items.map(item=>`<li>${escape(item)}</li>`).join('')}</ul></section>`).join('')}</div>`;
  } else {
    body = `<div class="learning-table-scroll" tabindex="0" role="region" aria-label="${escape(block.title)}"><table><thead><tr>${block.columns.map(column=>`<th scope="col">${escape(column)}</th>`).join('')}</tr></thead><tbody>${block.rows.map(row=>`<tr>${row.map((cell,index)=>index===0?`<th scope="row">${escape(cell)}</th>`:`<td>${escape(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  return `<figure class="concept-visual"><h3>${escape(block.title)}</h3>${body}<figcaption>${escape(block.caption)}</figcaption></figure>`;
}

export function plotGeometry(block) {
  const points = block.series.flatMap(series=>series.points);
  const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
  let minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
  if(minX===maxX){minX-=1;maxX+=1;}
  if(minY===maxY){minY-=1;maxY+=1;}
  const padding=(maxY-minY)*.08;
  minY-=padding;maxY+=padding;
  const x=value=>72+(value-minX)/(maxX-minX)*470;
  const y=value=>222-(value-minY)/(maxY-minY)*184;
  return {minX,maxX,minY,maxY,x,y};
}

export function renderPlot(block,serial) {
  const {minX,maxX,minY,maxY,x,y}=plotGeometry(block);
  const colors=['#245446','#97553a','#496e9e','#856231'];
  const dashes=['','7 4','2 4','10 3 2 3'];
  const ticks=Array.from({length:5},(_,i)=>i/4);
  const grid=ticks.map(fraction=>{
    const value=minY+fraction*(maxY-minY),py=y(value);
    return `<path d="M72 ${py}H542" stroke="#dce5d2"/><text x="61" y="${py+4}" text-anchor="end">${number(value)}</text>`;
  }).join('');
  const horizontal=ticks.map(fraction=>{
    const value=minX+fraction*(maxX-minX),px=x(value);
    return `<text x="${px}" y="244" text-anchor="middle">${number(value)}</text>`;
  }).join('');
  const lines=block.series.map((series,index)=>{
    const path=series.points.map((point,i)=>`${i?'L':'M'}${x(point[0]).toFixed(2)} ${y(point[1]).toFixed(2)}`).join(' ');
    return `<path d="${path}" fill="none" stroke="${colors[index%colors.length]}" stroke-width="2.5" stroke-dasharray="${dashes[index%dashes.length]}"/>${series.points.map(point=>`<circle cx="${x(point[0])}" cy="${y(point[1])}" r="3.5" fill="${colors[index%colors.length]}"/>`).join('')}`;
  }).join('');
  return `<figure class="data-plot"><h3>${escape(block.title)}</h3><ul class="plot-legend">${block.series.map((series,index)=>`<li><svg width="25" height="12" aria-hidden="true"><path d="M1 6H24" stroke="${colors[index%colors.length]}" stroke-width="3" stroke-dasharray="${dashes[index%dashes.length]}"/></svg>${escape(series.name)}</li>`).join('')}</ul><div class="figure-scroll" tabindex="0" role="region" aria-label="Graphique ${escape(block.title)}"><svg viewBox="0 0 600 300" role="img" aria-labelledby="plot-${serial}-title plot-${serial}-description"><title id="plot-${serial}-title">${escape(block.title)}</title><desc id="plot-${serial}-description">${escape(block.caption)} Les valeurs sont disponibles dans le tableau qui suit.</desc><g class="plot-ticks">${grid}${horizontal}</g><path d="M72 34V222H547" fill="none" stroke="#839779"/>${lines}<text x="307" y="281" text-anchor="middle" class="plot-axis">${escape(block.xLabel)}</text><text x="72" y="20" class="plot-axis">${escape(block.yLabel)}</text></svg></div><figcaption>${escape(block.caption)}</figcaption><details class="plot-values"><summary>Lire les valeurs du graphique</summary><div class="learning-table-scroll"><table><thead><tr><th scope="col">Série</th><th scope="col">${escape(block.xLabel)}</th><th scope="col">${escape(block.yLabel)}</th></tr></thead><tbody>${block.series.map(series=>series.points.map(point=>`<tr><th scope="row">${escape(series.name)}</th><td>${number(point[0])}</td><td>${number(point[1])}</td></tr>`).join('')).join('')}</tbody></table></div></details></figure>`;
}

function codeLines(block,step) {
  if(!block.code)return '';
  const active=new Set(step.lines??[]);
  return block.code.split('\n').map((line,index)=>`<span class="walk-code-line ${active.has(index+1)?'is-active':''}" data-line="${index+1}"><span class="line-number" aria-hidden="true">${index+1}</span><span>${escape(line)||' '}</span></span>`).join('');
}

function stepContent(step,index,total) {
  return `<p class="walk-position">ÉTAPE ${index+1} / ${total}</p><h4>${escape(step.title)}</h4><p>${escape(step.text)}</p>${step.state?`<div class="walk-state"><span>Ce qu’on obtient à cette étape</span><pre>${escape(step.state)}</pre></div>`:''}`;
}

export function renderWalkthrough(block,serial) {
  const first=block.steps[0];
  return `<section class="worked-example" data-walkthrough="${serial}"><header><p class="eyebrow">ON LE FAIT ENSEMBLE</p><h3>${escape(block.title)}</h3><p class="worked-goal">${escape(block.goal)}</p></header><div class="worked-layout ${block.code?'has-code':''}">${block.code?`<div class="walk-code"><div class="code-label">${escape(block.language??'python')} · LIGNES À SUIVRE</div><pre><code>${codeLines(block,first)}</code></pre><p class="walk-no-execution">Exemple expliqué à l’avance : aucun code n’est exécuté ici.</p></div>`:''}<div class="walk-explanation" aria-live="polite" aria-atomic="true">${stepContent(first,0,block.steps.length)}</div></div><nav class="walk-controls" aria-label="Étapes de ${escape(block.title)}"><button type="button" data-walk-prev disabled>← Étape précédente</button><button type="button" data-walk-next>Étape suivante →</button></nav><details class="all-walk-steps"><summary>Voir toutes les étapes à la suite</summary><ol>${block.steps.map(step=>`<li><h4>${escape(step.title)}</h4><p>${escape(step.text)}</p>${step.state?`<pre>${escape(step.state)}</pre>`:''}</li>`).join('')}</ol></details><p class="worked-result"><strong>Ce que cela nous apprend.</strong> ${escape(block.result)}</p></section>`;
}

export function attachWalkthroughs(root,blocks) {
  const walkthroughs=blocks.filter(block=>block.type==='walkthrough');
  root.querySelectorAll('[data-walkthrough]').forEach((section,index)=>{
    const block=walkthroughs[index];
    let current=0;
    const previous=section.querySelector('[data-walk-prev]'),next=section.querySelector('[data-walk-next]');
    function update(delta){
      current=Math.max(0,Math.min(block.steps.length-1,current+delta));
      const step=block.steps[current];
      section.querySelector('.walk-explanation').innerHTML=stepContent(step,current,block.steps.length);
      if(block.code)section.querySelector('.walk-code code').innerHTML=codeLines(block,step);
      previous.disabled=current===0;next.disabled=current===block.steps.length-1;
      section.dataset.step=String(current);
    }
    previous.addEventListener('click',()=>update(-1));next.addEventListener('click',()=>update(1));
  });
}

export function renderCheckpoint(checkpoint) {
  return `<section class="lesson-checkpoint"><p class="eyebrow">FAIRE UN PETIT PAS SANS LE MODÈLE</p><h2>Est-ce que l’idée tient ?</h2><p class="checkpoint-intro">Essayez sur une situation un peu différente. Ce QCM est facultatif et ne compte pas dans votre session de quiz.</p><h3>${escape(checkpoint.prompt)}</h3><div class="checkpoint-options">${shuffle(checkpoint.options).map((option,index)=>`<button type="button" data-checkpoint-option="${escape(option.id)}"><span class="checkpoint-letter" aria-hidden="true">${String.fromCharCode(65+index)}</span><span>${escape(option.text)}</span></button>`).join('')}</div><div class="checkpoint-feedback" role="status" hidden></div><button type="button" class="checkpoint-reset" hidden>Réessayer ce repère</button></section>`;
}

export function attachCheckpoint(root,checkpoint) {
  const section=root.querySelector('.lesson-checkpoint');
  if(!section)return;
  const buttons=[...section.querySelectorAll('[data-checkpoint-option]')],feedback=section.querySelector('.checkpoint-feedback'),reset=section.querySelector('.checkpoint-reset');
  let locked=false;
  for(const button of buttons)button.addEventListener('click',()=>{
    if(locked)return;
    locked=true;
    const chosen=button.dataset.checkpointOption;
    for(const option of buttons){
      const id=option.dataset.checkpointOption;
      option.disabled=true;
      if(id===checkpoint.correctOptionId){option.classList.add('is-correct');option.insertAdjacentHTML('beforeend','<strong class="checkpoint-result-label">✓ Bonne réponse</strong>');}
      else if(id===chosen){option.classList.add('is-wrong');option.insertAdjacentHTML('beforeend','<strong class="checkpoint-result-label">× Votre réponse</strong>');}
    }
    feedback.hidden=false;
    feedback.innerHTML=`<strong>${chosen===checkpoint.correctOptionId?'✓ L’idée est là.':'↳ Regardons ce qui change.'}</strong><p>${escape(checkpoint.explanation)}</p>`;
    reset.hidden=false;
  });
  reset.addEventListener('click',()=>{
    locked=false;
    for(const button of buttons){button.disabled=false;button.classList.remove('is-correct','is-wrong');button.querySelector('.checkpoint-result-label')?.remove();}
    feedback.hidden=true;reset.hidden=true;buttons[0].focus();
  });
}
