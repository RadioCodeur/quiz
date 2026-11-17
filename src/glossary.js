import './style.css';
import './glossary.css';
import {filterTerms} from './glossary-model.js';
import {courseHref} from './course-model.js';
const root=document.querySelector('#app');
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
try {
  const response=await fetch(`${import.meta.env.BASE_URL}glossary.json`,{cache:'no-cache'});
  if(!response.ok)throw new Error('Le glossaire est indisponible.');
  const {terms}=await response.json();
  const categories=[...new Set(terms.map(term=>term.category))];
  root.innerHTML=`<section class="glossary-heading"><p class="eyebrow">LES MOTS, DANS LES DEUX SENS</p><h1>Un terme vous arrête ?</h1><p>Retrouvez son sens en français, son nom anglais et le chapitre qui l’explique avec un exemple.</p></section><form class="glossary-search" role="search"><label for="term-search">Terme français ou anglais<input id="term-search" type="search" placeholder="Ex. gradient, batch, décibel…" autocomplete="off"></label><label for="term-category">Domaine<select id="term-category"><option value="">Tous les domaines</option>${categories.map(category=>`<option value="${esc(category)}">${esc(category)}</option>`).join('')}</select></label><button class="button secondary" type="reset">Effacer</button></form><p id="term-count" role="status" aria-live="polite"></p><dl class="glossary-terms"></dl><p class="glossary-note">Les définitions servent de repères. Les hypothèses, exemples et sources se trouvent dans les chapitres liés.</p>`;
  const input=root.querySelector('#term-search'),select=root.querySelector('#term-category');
  const params=new URLSearchParams(location.search);
  input.value=params.get('q')??'';
  select.value=categories.includes(params.get('domain'))?params.get('domain'):'';
  function update(){
    const visible=filterTerms(terms,input.value,select.value);
    root.querySelector('#term-count').textContent=`${visible.length} terme${visible.length===1?'':'s'} sur ${terms.length}`;
    root.querySelector('.glossary-terms').innerHTML=visible.map(term=>`<div class="glossary-term" id="${esc(term.id)}"><dt><span>${esc(term.fr)}</span><span lang="en">${esc(term.en)}</span></dt><dd><p>${esc(term.definition)}</p><a href="${esc(courseHref(term.themeId,term.chapterId))}">Comprendre avec le cours →</a><small>${esc(term.category)}</small></dd></div>`).join('')||'<div class="glossary-empty"><dt>Aucun terme trouvé.</dt><dd>Essayez un mot plus court ou un autre domaine.</dd></div>';
    const query=new URLSearchParams();
    if(input.value.trim())query.set('q',input.value.trim());
    if(select.value)query.set('domain',select.value);
    history.replaceState(null,'',`${location.pathname}${query.size?'?'+query:''}${location.hash}`);
  }
  root.querySelector('form').addEventListener('submit',event=>event.preventDefault());
  input.addEventListener('input',update);select.addEventListener('change',update);
  root.querySelector('form').addEventListener('reset',()=>{input.value='';select.value='';update();});
  update();
}catch(error){root.innerHTML=`<p class="notice" role="alert">${esc(error.message)} <a href="./cours.html">Retrouver les cours</a></p>`;}
