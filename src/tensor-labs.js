const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
const fmt=value=>typeof value==='number'?Number(value.toFixed(6)).toLocaleString('fr-FR'):typeof value==='boolean'?(value?'True':'False'):String(value);
export const LAB_KINDS=['axes','reshape','broadcast','linear','gradient','padding','conv'];
export function calculateLab(kind,state={},block={}) {
  if(kind==='axes'){
    const matrix=[[1.5,-1.5],[4.5,-4.5],[2.5,-2.5]],axis=Number(state.axis??1);
    const groups=axis===1?matrix:[matrix.map(row=>row[0]),matrix.map(row=>row[1])];
    return {matrix,axis,groups,result:groups.map(values=>values.indexOf(Math.max(...values))),shape:axis===1?[3]:[2]};
  }
  if(kind==='reshape')return {original:[[1,2,3],[4,5,6]],reshape:[[1,2],[3,4],[5,6]],transpose:[[1,4],[2,5],[3,6]],value:Number(state.value??4)};
  if(kind==='broadcast'){
    const matrix=block.input??[[1,2],[3,4],[5,6]],reference=[Number(state.r0??block.reference?.[0]??3),Number(state.r1??block.reference?.[1]??4)];
    return {matrix,reference,expanded:matrix.map(()=>[...reference]),result:matrix.map(row=>row.map((value,i)=>value-reference[i]))};
  }
  if(kind==='linear'){
    const input=[.1,1.5],weights=[Number(state.w0??0),Number(state.w1??1)],bias=Number(state.bias??0),products=input.map((value,i)=>value*weights[i]);
    return {input,weights,bias,products,result:products.reduce((sum,value)=>sum+value,0)+bias};
  }
  if(kind==='gradient'){
    const weight=Number(state.weight??0),rate=Number(state.rate??.1),loss=(weight-2)**2,gradient=2*(weight-2),next=weight-rate*gradient;
    return {weight,rate,loss,gradient,next,nextLoss:(next-2)**2};
  }
  if(kind==='padding'){
    const matrix=[[2,4],[6,0]],mask=[[true,true],[true,false]],masked=String(state.masked??'true')==='true';
    return {matrix,mask,masked,numerators:[6,6],denominators:masked?[2,1]:[2,2],result:masked?[3,6]:[3,3]};
  }
  if(kind==='conv'){
    const input=block.input??[[1,2,3],[4,5,6],[7,8,9]],kernel=(block.kernel??[[1,0],[0,-1]]).map(line=>[...line]),position=Math.max(0,Math.min(3,Number(state.position??0))),row=Math.floor(position/2),col=position%2;
    kernel[0][0]=Number(state.w00??kernel[0][0]);
    const products=kernel.map((line,i)=>line.map((weight,j)=>input[row+i][col+j]*weight));
    const result=products.flat().reduce((sum,value)=>sum+value,0);
    const output=[0,1].map(i=>[0,1].map(j=>kernel.flatMap((line,r)=>line.map((weight,c)=>weight*input[i+r][j+c])).reduce((sum,value)=>sum+value,0)));
    return {input,kernel,position,row,col,products,result,output};
  }
  throw new Error('Calcul pédagogique inconnu');
}

function matrix(values,title,{columns,rows,selected,active,padded=false,clickable=false}={}) {
  return `<figure class="lab-matrix"><figcaption>${esc(title)}</figcaption><div class="learning-table-scroll" tabindex="0"><table><thead><tr><th scope="col">Ligne / colonne</th>${values[0].map((_,i)=>`<th scope="col">${esc(columns?.[i]??i)}</th>`).join('')}</tr></thead><tbody>${values.map((line,r)=>`<tr><th scope="row">${esc(rows?.[r]??r)}</th>${line.map((value,c)=>{
    const chosen=selected===value,highlight=active?.(r,c),padding=padded&&r===1&&c===1;
    const content=clickable?`<button type="button" data-follow-value="${esc(value)}" aria-pressed="${chosen}">${fmt(value)}${chosen?' ←':''}</button>`:`${fmt(value)}${chosen?' ←':''}`;
    return `<td class="${chosen?'tracked-cell ':''}${highlight?'active-cell ':''}${padding?'padding-cell':''}">${content}${padding?'<span class="sr-only"> ajouté, hors signal</span>':''}</td>`;
  }).join('')}</tr>`).join('')}</tbody></table></div></figure>`;
}
function scalarTable(rows){return `<div class="learning-table-scroll" tabindex="0"><table><thead><tr><th scope="col">Quantité</th><th scope="col">Valeur</th></tr></thead><tbody>${rows.map(([name,value])=>`<tr><th scope="row">${esc(name)}</th><td>${esc(value)}</td></tr>`).join('')}</tbody></table></div>`;}
function curve(value){
  const low=Math.min(-1,value.weight,value.next),high=Math.max(5,value.weight,value.next),maxY=Math.max(10,value.loss,value.nextLoss)*1.15;
  const x=n=>45+(n-low)/(high-low)*450,y=n=>210-n/maxY*175;
  const points=Array.from({length:81},(_,i)=>{const w=low+(high-low)*i/80;return `${i?'L':'M'}${x(w)},${y((w-2)**2)}`;}).join(' ');
  const tangent=[value.weight-.25,value.weight+.25].map((w,i)=>`${i?'L':'M'}${x(w)},${y(value.loss+value.gradient*(w-value.weight))}`).join(' ');
  return `<svg class="lab-curve" viewBox="0 0 550 265" role="img" aria-label="Courbe de perte, tangente et prochain poids"><path d="M45 25V210H510" fill="none" stroke="#53654c"/><path d="${points}" fill="none" stroke="#245446" stroke-width="3"/><path d="${tangent}" fill="none" stroke="#9a5535" stroke-width="3" stroke-dasharray="5 3"/><circle cx="${x(value.weight)}" cy="${y(value.loss)}" r="6" fill="#245446"/><path d="M${x(value.weight)},${y(value.loss)}L${x(value.next)},${y(value.nextLoss)}" stroke="#866532" stroke-width="2" stroke-dasharray="3 3"/><rect x="${x(value.next)-5}" y="${y(value.nextLoss)-5}" width="10" height="10" fill="#866532"/><text x="45" y="18">Perte (w−2)²</text><text x="230" y="250">Poids w</text><text x="${x(2)}" y="230" text-anchor="middle">2</text></svg><p>Cercle : point courant. Carré : point après le pas. Trait court pointillé : tangente locale.</p>`;
}
function output(kind,state,block){
  const v=calculateLab(kind,state,block);
  if(kind==='axes')return matrix(v.matrix,'Scores choisis à la main · forme (3,2)',{columns:['Voix 0','Percussion 1'],rows:['A · voix','B · percussion','C · voix']})+`<p><strong>argmax(dim=${v.axis}) → [${v.result.join(', ')}], forme (${v.shape[0]},).</strong></p><ol>${v.groups.map((values,i)=>`<li>${v.axis===1?'Extrait':'Classe'} ${i} : comparer [${values.map(fmt).join(' ; ')}] → maximum ${fmt(Math.max(...values))}, position ${v.result[i]}.</li>`).join('')}</ol><p>Les scores ne changent pas. Le résultat désigne ${v.axis===1?'une classe pour chacun des trois extraits':'un extrait pour chacune des deux classes'}.</p>`;
  if(kind==='reshape')return `<p>Valeur suivie : <strong>${v.value}</strong>. Les flèches et bordures repèrent la même case.</p><div class="lab-grids">${matrix(v.original,'Source (2,3)',{selected:v.value,clickable:true})}${matrix(v.reshape,'reshape(3,2)',{selected:v.value,clickable:true})}${matrix(v.transpose,'transpose(0,1)',{selected:v.value,clickable:true})}</div>`;
  if(kind==='broadcast')return `<div class="lab-grids">${matrix(v.matrix,'X · forme (3,2)',{columns:block.columns,rows:block.rows})}${matrix(v.expanded,'Référence alignée logiquement · (3,2)',{columns:block.columns,rows:block.rows})}${matrix(v.result,'X − référence · forme (3,2)',{columns:block.columns,rows:block.rows})}</div><p>La référence stockée reste [${v.reference.map(fmt).join(' ; ')}], forme (1,2). L’affichage répète son alignement ; il n’affirme pas que trois copies sont stockées.</p>`;
  if(kind==='linear')return scalarTable([['RMS × poids RMS',`${fmt(v.input[0])} × ${fmt(v.weights[0])} = ${fmt(v.products[0])}`],['Crête × poids crête',`${fmt(v.input[1])} × ${fmt(v.weights[1])} = ${fmt(v.products[1])}`],['Biais',fmt(v.bias)],['Score voix A',`${fmt(v.products[0])} + ${fmt(v.products[1])} + ${fmt(v.bias)} = ${fmt(v.result)}`]])+'<p>Une seule sortie est ouverte ici. Dans Linear(2,2), la seconde ligne de poids calcule indépendamment le score percussion.</p>';
  if(kind==='gradient')return curve(v)+scalarTable([['Poids courant',fmt(v.weight)],['Perte courante',fmt(v.loss)],['Pente : 2(w−2)',fmt(v.gradient)],['Pas : −taux × pente',fmt(-v.rate*v.gradient)],['Nouveau poids',fmt(v.next)],['Perte recalculée',fmt(v.nextLoss)]])+`<p>${v.nextLoss>v.loss?'Ce pas augmente la perte : sa longueur a dépassé une région favorable.':v.nextLoss===v.loss?'Le coût reste identique avec ce choix de pas.':'Ce pas diminue la perte dans cet exemple.'}</p>`;
  if(kind==='padding')return matrix(v.matrix,'Séquences complétées · cases ajoutées hachurées',{padded:true,columns:['Trame 0','Trame 1'],rows:['Extrait A','Extrait B']})+matrix(v.mask,'Masque des positions réelles',{columns:['Trame 0','Trame 1'],rows:['Extrait A','Extrait B']})+scalarTable(v.result.map((result,i)=>[`Séquence ${i}`,`${v.numerators[i]} / ${v.denominators[i]} = ${fmt(result)}`]))+`<p>${v.masked?'La seconde séquence garde un dénominateur de un.':'La moyenne naïve compte la case ajoutée et divise aussi la seconde somme par deux.'}</p>`;
  if(kind==='conv')return `<div class="lab-grids">${matrix(v.input,'Entrée · cases utilisées marquées',{active:(r,c)=>r>=v.row&&r<v.row+2&&c>=v.col&&c<v.col+2})}${matrix(v.kernel,'Noyau 2×2')}${matrix(v.products,'Produits à la position choisie')}</div><p>Position du coin supérieur gauche : (${v.row},${v.col}). Somme des produits : ${v.products.flat().map(fmt).join(' + ')} = <strong>${fmt(v.result)}</strong>.</p>${matrix(v.output,'Sortie complète · forme (2,2)',{active:(r,c)=>r===v.row&&c===v.col})}<p>Le noyau est appliqué sans retournement, comme la corrélation utilisée par Conv2d. Aucun paramètre n’est appris dans cette simulation.</p>`;
}
function controls(kind,serial,block={}){
  const select=(key,label,options)=>`<label for="lab-${serial}-${key}">${label}<select id="lab-${serial}-${key}" data-lab-control="${key}">${options.map(([value,text])=>`<option value="${value}">${text}</option>`).join('')}</select></label>`;
  const numeric=(key,label,value,min,max,step)=>`<label for="lab-${serial}-${key}">${label}<input id="lab-${serial}-${key}" data-lab-control="${key}" type="number" value="${value}" min="${min}" max="${max}" step="${step}"></label>`;
  if(kind==='axes')return select('axis','Axe réduit',[[1,'dim=1 · comparer les classes par extrait'],[0,'dim=0 · comparer les extraits par classe']]);
  if(kind==='reshape')return select('value','Valeur à suivre',[1,2,3,4,5,6].map(value=>[value,value]));
  if(kind==='broadcast')return numeric('r0','Référence colonne 0',block.reference?.[0]??3,-20,20,'any')+numeric('r1','Référence colonne 1',block.reference?.[1]??4,-20,20,'any');
  if(kind==='linear')return numeric('w0','Poids RMS',0,-20,20,.5)+numeric('w1','Poids facteur de crête',1,-20,20,.5)+numeric('bias','Biais',0,-20,20,.5);
  if(kind==='gradient')return numeric('weight','Poids courant w',0,-1,5,.1)+numeric('rate','Taux du pas',.1,0,1.5,.1);
  if(kind==='padding')return select('masked','Calculer la moyenne',[[true,'Avec masque : compter seulement le réel'],[false,'Sans masque : compter aussi le remplissage']]);
  if(kind==='conv')return select('position','Position du noyau',[[0,'Coin (0,0)'],[1,'Coin (0,1)'],[2,'Coin (1,0)'],[3,'Coin (1,1)']])+numeric('w00','Poids du coin supérieur gauche',block.kernel?.[0]?.[0]??1,-5,5,.5);
}
export function renderTensorLab(block,serial){
  if(!LAB_KINDS.includes(block.kind))throw new Error('Visualisation inconnue');
  return `<section class="tensor-lab" data-tensor-lab="${serial}"><h3>${esc(block.title)}</h3><p>${esc(block.caption)}</p><div class="lab-controls">${controls(block.kind,serial,block)}</div><div class="lab-output" aria-live="polite">${output(block.kind,{},block)}</div><p class="lab-runtime">Calcul pédagogique en JavaScript, sans interpréteur Python ni modèle PyTorch dans la page.</p></section>`;
}
export function attachTensorLabs(root,blocks){
  const labs=blocks.filter(block=>block.type==='tensor-lab');
  root.querySelectorAll('[data-tensor-lab]').forEach((section,index)=>{
    const block=labs[index],state={};
    section.querySelectorAll('[data-lab-control]').forEach(control=>{
      if(block.kind==='reshape')control.value='4';
      state[control.dataset.labControl]=control.value;
      control.addEventListener('input',()=>{
        if(control.type==='number'&&!Number.isFinite(control.valueAsNumber))return;
        if(control.type==='number'&&!control.validity.valid)return;
        state[control.dataset.labControl]=control.value;
        section.querySelector('.lab-output').innerHTML=output(block.kind,state,block);
      });
    });
    section.addEventListener('click',event=>{
      const cell=event.target.closest('[data-follow-value]');if(!cell)return;
      state.value=cell.dataset.followValue;section.querySelector('[data-lab-control="value"]').value=state.value;
      section.querySelector('.lab-output').innerHTML=output(block.kind,state,block);
      section.querySelector(`[data-follow-value="${state.value}"]`).focus({preventScroll:true});
    });
    section.querySelector('.lab-output').innerHTML=output(block.kind,state,block);
  });
}
