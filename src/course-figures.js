const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' })[c]);
export const FIGURE_KINDS = ['tensor-axes','broadcast','training-loop','sampling','stft','mel','pipeline','augmentation','generative-families','conditioning','lora','split','evaluation'];
const text = (x, y, value, extra = '') => `<text x="${x}" y="${y}" ${extra}>${esc(value)}</text>`;
const rect = (x,y,w,h,fill='var(--diagram-light)') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="11" fill="${fill}"/>`;
const arrow = (x1,y1,x2,y2) => `<path d="M${x1} ${y1} L${x2} ${y2}" fill="none" stroke="var(--diagram-ink)" stroke-width="2" marker-end="url(#arrow-head)"/>`;
function box(x,y,w,label,sub,fill) { return rect(x,y,w,65,fill)+text(x+w/2,y+27,label,'text-anchor="middle" font-weight="650"')+text(x+w/2,y+48,sub,'text-anchor="middle" class="diagram-small"'); }
function row(labels, y=70) {
  const w=150, gap=55, start=(640-(labels.length*w+(labels.length-1)*gap))/2;
  return labels.map(([label,sub],i)=>box(start+i*(w+gap),y,w,label,sub)+(i<labels.length-1?arrow(start+i*(w+gap)+w+8,y+32,start+(i+1)*(w+gap)-10,y+32):'')).join('');
}
function sinePath(f=4, offset=0, amplitude=40, length=560, y=120) {
  return Array.from({length:141},(_,i)=>`${i?'L':'M'}${40+i*length/140} ${(y-amplitude*Math.sin(2*Math.PI*f*i/140+offset)).toFixed(2)}`).join(' ');
}
function content(kind) {
  if(kind==='sampling') {
    return text(40,30,'Une onde continue, puis des mesures à intervalles réguliers.')+`<path d="${sinePath(3)}" fill="none" stroke="#809b71" stroke-width="3"/>`+
      Array.from({length:19},(_,i)=>{const x=40+i*560/18,y=120-40*Math.sin(2*Math.PI*3*i/18);return `<path d="M${x} 170V${y}" stroke="#c3ceb8"/><circle cx="${x}" cy="${y}" r="5" fill="#285648"/>`;}).join('')+
      `<path d="M35 170H610" stroke="#a8b69c"/>`+text(40,203,'Un point = un échantillon')+text(600,203,'temps →','text-anchor="end"')+text(40,235,'La fréquence d’échantillonnage décrit le nombre de points par seconde.','class="diagram-small"');
  }
  if(kind==='stft') {
    return text(35,28,'La STFT écoute le signal par petites fenêtres qui se chevauchent.')+`<path d="${sinePath(6,0,25,560,80)}" fill="none" stroke="#607e58" stroke-width="2"/>`+
      [0,1,2,3,4].map(i=>`<rect x="${55+i*100}" y="42" width="145" height="75" rx="6" fill="#d7e6c2" fill-opacity=".35" stroke="#688551"/>`).join('')+
      text(55,145,'← fenêtre →')+arrow(100,153,200,153)+text(108,177,'hop','class="diagram-small"')+
      text(375,150,'FFT de chaque fenêtre')+arrow(475,160,475,185)+
      Array.from({length:14},(_,x)=>Array.from({length:4},(_,y)=>`<rect x="${350+x*17}" y="${194+y*11}" width="16" height="10" fill="hsl(${85+x*2} 25% ${30+((x*13+y*19)%50)}%)"/>`).join('')).join('')+
      text(35,220,'Fenêtre : détail fréquentiel.','class="diagram-small"')+text(35,241,'Hop : espacement des analyses.','class="diagram-small"');
  }
  if(kind==='mel') {
    return text(35,30,'Les bandes mel regroupent l’énergie ; elles ne conservent pas la phase.')+
      Array.from({length:7},(_,i)=>{const a=40+((i/7)**1.6)*530,b=40+(((i+1)/7)**1.6)*530,c=40+(((i+2)/7)**1.6)*530;return `<path d="M${a} 175 L${b} 65 L${Math.min(c,610)} 175" stroke="hsl(${95+i*8} 24% 42%)" fill="hsl(${95+i*8} 24% 65% / .15)" stroke-width="2"/>`;}).join('')+
      text(40,205,'fréquences basses')+text(600,205,'fréquences hautes →','text-anchor="end"')+text(40,239,'Schéma qualitatif : les bandes s’élargissent vers les hautes fréquences.','class="diagram-small"');
  }
  if(kind==='tensor-axes') {
    return text(35,30,'Un tenseur audio : chaque axe a un rôle.')+row([['B = 4','quatre extraits'],['C = 1','un canal mono'],['T = 16 000','échantillons / extrait']])+
      rect(105,170,430,55)+text(320,204,'(B, C, T) = (4, 1, 16 000)','text-anchor="middle" font-family="monospace"')+text(320,249,'Changer l’ordre des axes change ce qu’ils signifient.','text-anchor="middle" class="diagram-small"');
  }
  if(kind==='broadcast') {
    return text(35,30,'Broadcasting : comparer les axes en partant de la droite.')+
      text(60,90,'batch de spectres')+text(60,136,'biais par fréquence')+
      [4,3,7].map((n,i)=>rect(310+i*76,62,62,44)+text(341+i*76,90,n,'text-anchor="middle"')).join('')+
      [1,3,1].map((n,i)=>rect(310+i*76,110,62,44,'#dce9c8')+text(341+i*76,138,n,'text-anchor="middle"')).join('')+
      text(320,197,'4 × 3 × 7 + 1 × 3 × 1 → 4 × 3 × 7','text-anchor="middle" font-family="monospace"')+text(320,235,'Un axe de taille 1 peut s’étendre ; deux autres tailles doivent coïncider.','text-anchor="middle" class="diagram-small"');
  }
  if(kind==='training-loop') {
    return text(35,30,'Entraîner : mesurer une erreur, puis déplacer les paramètres.')+row([['Prédiction','model(x)'],['Perte','criterion(pred, y)'],['Gradients','loss.backward()']])+
      box(220,174,200,'Mise à jour','optimizer.step()','#dce9c8')+arrow(525,143,425,191)+arrow(210,205,110,145)+text(320,158,'zero_grad() avant l’accumulation choisie','text-anchor="middle" class="diagram-small"');
  }
  if(kind==='pipeline') {
    return text(35,30,'Exemple : reconnaître une sirène dans un enregistrement.')+row([['Audio','signal rééchantillonné'],['Représentation','log-mel ou encodeur'],['Prédiction','scores de classes']])+
      rect(70,178,500,54)+text(320,201,'Même préparation pour entraîner et pour utiliser le modèle.','text-anchor="middle"')+text(320,221,'Normalisation ajustée sur le train uniquement.','text-anchor="middle" class="diagram-small"');
  }
  if(kind==='augmentation') {
    return text(35,30,'L’augmentation doit préserver le sens de la cible.')+box(50,68,230,'Détection de sirène','bruit modéré : cible inchangée')+box(355,68,230,'Reconnaissance de hauteur','transposer : cible à adapter','#f0e4d1')+
      text(320,188,'Même transformation, validité différente selon la tâche.','text-anchor="middle"')+text(320,224,'Un masque de spectrogramme ne remplace pas une vérification des labels.','text-anchor="middle" class="diagram-small"');
  }
  if(kind==='generative-families') {
    return text(35,28,'Trois manières d’organiser la génération audio.')+
      box(40,63,170,'Autoencodeur','audio ↔ latent')+box(235,63,170,'Autorégressif','token après token')+box(430,63,170,'Diffusion','bruit → débruitages')+
      text(125,164,'Apprendre une','text-anchor="middle"')+text(125,186,'représentation.','text-anchor="middle"')+
      text(320,164,'Prédire la suite','text-anchor="middle"')+text(320,186,'à partir du passé.','text-anchor="middle"')+
      text(515,164,'Affiner une','text-anchor="middle"')+text(515,186,'proposition bruitée.','text-anchor="middle"')+
      text(320,238,'Ces briques peuvent se combiner : codec + modèle de tokens, par exemple.','text-anchor="middle" class="diagram-small"');
  }
  if(kind==='conditioning') {
    return text(35,30,'Contrôler le son : préciser quoi, quand et avec quelle marge de liberté.')+
      box(40,65,155,'Texte','intention globale')+box(242,65,155,'Notes / partition','événements datés')+box(445,65,155,'Audio / courbe','matière et évolution')+
      arrow(120,140,235,189)+arrow(320,140,320,180)+arrow(525,140,405,189)+box(225,183,190,'Générateur','conditions alignées','#dce9c8');
  }
  if(kind==='lora') {
    return text(35,30,'LoRA : conserver les poids de base, apprendre une mise à jour de petit rang.')+
      box(50,80,155,'W₀ gelée','d_out × d_in')+text(231,119,'+','font-size="30"')+box(270,80,125,'B','d_out × r','#dce9c8')+text(410,119,'×','font-size="25"')+box(445,80,140,'A','r × d_in','#dce9c8')+
      text(320,201,'W = W₀ + B A','text-anchor="middle" font-size="24"')+text(320,242,'r est petit : moins de paramètres entraînés, mais une base toujours à faire tourner.','text-anchor="middle" class="diagram-small"');
  }
  if(kind==='split') {
    return text(35,30,'On sépare les enregistrements avant de fabriquer leurs extraits.')+row([['Train','apprendre les poids'],['Validation','choisir les réglages'],['Test','évaluer à la fin']])+
      rect(45,175,550,60,'#f0e4d1')+text(320,200,'Un enregistrement et ses extraits restent dans le même ensemble.','text-anchor="middle"')+text(320,222,'Selon l’usage, on peut aussi devoir grouper par interprète ou appareil.','text-anchor="middle" class="diagram-small"');
  }
  if(kind==='evaluation') {
    return text(35,30,'Un générateur audio se juge sur plusieurs axes.')+
      box(45,68,165,'Qualité','artefacts et naturel')+box(238,68,165,'Contrôle','respect de la consigne')+box(430,68,165,'Coût','temps, mémoire, calcul')+
      text(320,186,'Mesures automatiques + écoute + protocole documenté','text-anchor="middle"')+text(320,230,'Une amélioration sur un axe ne garantit pas une amélioration sur les autres.','text-anchor="middle" class="diagram-small"');
  }
  return '';
}

export function renderFigure(kind, caption, serial) {
  const illustration = content(kind).replaceAll('url(#arrow-head)',`url(#arrow-head-${serial})`);
  return `<figure class="lesson-figure"><div class="figure-scroll" tabindex="0" role="group" aria-label="Schéma ${esc(caption)}"><svg viewBox="0 0 640 270" role="img" aria-labelledby="figure-title-${serial}" xmlns="http://www.w3.org/2000/svg"><title id="figure-title-${serial}">${esc(caption)}</title><defs><marker id="arrow-head-${serial}" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="var(--diagram-ink)"/></marker></defs>${illustration}</svg></div><figcaption>${esc(caption)}<span class="figure-help">↔ Faites glisser le schéma pour en voir la suite.</span></figcaption></figure>`;
}
