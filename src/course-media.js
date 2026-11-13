const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const fmt=(value,digits=3)=>Number.isFinite(value)?new Intl.NumberFormat('fr-FR',{maximumFractionDigits:digits}).format(value):'−∞';

export const LAB_VIEWS={
  overview:{variants:['original'],display:'waveform'},
  level:{variants:['original','quiet','rms-matched','clipped'],display:'waveform'},
  resample:{variants:['original','resampled','lowpass'],display:'spectrogram'},
  stft:{variants:['original','resampled'],display:'spectrogram'},
  mel:{variants:['original','resampled'],display:'mel'},
  phase:{variants:['original','polarity-inverted','cancelled','phase-random'],display:'spectrogram'},
  augmentation:{variants:['original','quiet','lowpass','clipped'],display:'spectrogram'},
};
const DISPLAY_NAMES={waveform:'Forme d’onde',spectrogram:'Spectrogramme STFT',mel:'Spectrogramme mel'};
const FIGURE_READINGS={
  waveform:'Horizontalement : les quatre secondes du fichier. Verticalement : les amplitudes numériques, avec la même limite ±1 pour toutes les versions. La vue d’ensemble conserve les minima et maxima de petites tranches afin de ne pas effacer les pics ; elle ne dessine pas séparément les 192 000 valeurs.',
  spectrogram:'Chaque colonne analyse une fenêtre de Hann de 25 ms ; les centres sont espacés de 10 ms. Le temps est horizontal, la fréquence verticale. Les couleurs claires indiquent un carré de magnitude spectrale plus élevé : P = |STFT / somme(fenêtre)|², affiché de −100 à 0 dB avec la référence fixe 1. Ce ne sont pas des dB SPL ni le RMS dBFS du fichier. La zone hachurée est hors bande pour la version à 16 kHz.',
  mel:'Le temps est horizontal ; les 64 bandes verticales regroupent les puissances STFT avec des filtres Slaney normalisés en aire, entre 0 et 8 kHz. Les graduations restent en hertz mais leur espacement suit l’échelle mel. La couleur vaut 10 log10(M/1), avec la même référence entre versions ; le plancher d’affichage est −100 dB. La pondération des filtres empêche de lire une couleur STFT et une couleur mel comme deux mesures identiques.'
};
const figureReading=(catalog,key)=>catalog.figureDescriptions?.[key]??FIGURE_READINGS[key];
export function mediaUrl(path,base='./') {
  if(typeof path!=='string'||!/^media\/[a-zA-Z0-9_./-]+$/.test(path)||path.split('/').includes('..'))throw new Error('Chemin média local invalide');
  return `${base}${path}`;
}
function credit(source){
  return `<p class="media-credit">${esc(source.author)} · <a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">${esc(source.title)}</a> · <a href="${esc(source.licenseUrl)}" target="_blank" rel="noopener noreferrer">${esc(source.license)}</a>${source.changes?`<span>${esc(source.changes)}</span>`:''}</p>`;
}
export function renderIllustration(block,catalog,base='./') {
  const asset=catalog.images.find(item=>item.id===block.assetId);
  if(!asset)return '<p class="notice">Cette illustration est momentanément indisponible.</p>';
  const src=mediaUrl(asset.src,base);
  return `<figure class="course-illustration"><h3>${esc(block.title??asset.title)}</h3><a class="illustration-enlarge" href="${esc(src)}" target="_blank" rel="noopener noreferrer" aria-label="Agrandir : ${esc(asset.title)}"><img src="${esc(src)}" alt="${esc(asset.alt)}" loading="lazy" decoding="async"><span>Agrandir l’image ↗</span></a><figcaption><p>${esc(block.caption??asset.caption)}</p><div class="image-reading"><strong>Comment la lire</strong><ol>${(block.reading??asset.reading).map(item=>`<li>${esc(item)}</li>`).join('')}</ol></div>${credit(asset.credit)}</figcaption></figure>`;
}
export function labOptions(block,catalog) {
  const spec=LAB_VIEWS[block.view];
  if(!spec)return [];
  return spec.variants.filter(id=>catalog.clips.every(clip=>clip.variants.some(variant=>variant.id===id)));
}
function metrics(variant,original) {
  const m=variant.metrics;
  const delta=Number.isFinite(m.rmsDbfs)&&Number.isFinite(original.metrics.rmsDbfs)?m.rmsDbfs-original.metrics.rmsDbfs:null;
  return `<details class="lab-measures"><summary>Les mesures de ce fichier</summary><dl><div><dt>Crête |x|max</dt><dd>${fmt(m.peak,4)}</dd></div><div><dt>RMS</dt><dd>${fmt(m.rms,4)}</dd></div><div><dt>Moyenne x²</dt><dd>${fmt(m.meanSquare,6)}</dd></div><div><dt>Niveau de crête</dt><dd>${fmt(m.peakDbfs,2)} dBFS</dd></div><div><dt>Niveau RMS, réf. 1</dt><dd>${fmt(m.rmsDbfs,2)} dBFS</dd></div><div><dt>Facteur de crête</dt><dd>${m.crestDb===null?'Indéfini (silence)':`${fmt(m.crestDb,2)} dB`}</dd></div><div><dt>Écart RMS à l’original</dt><dd>${fmt(delta,2)} dB</dd></div></dl><p>Mesures sur toute la durée du WAV livré. Référence numérique : amplitude 1, y compris pour le RMS. Aucune mesure en dB SPL ni estimation de sonie en LUFS.</p></details>`;
}
function labDisplay(block,catalog,variantId,display,base){
  return catalog.clips.map(clip=>{
    const original=clip.variants.find(item=>item.id==='original');
    const variant=clip.variants.find(item=>item.id===variantId)??original;
    const source=catalog.sources.find(item=>item.id===clip.sourceId);
    const figure=variant.figures[display];
    return `<article class="lab-clip"><header><h4>${esc(clip.label)}</h4><p>${esc(variant.label)} · ${fmt(variant.duration,2)} s · ${fmt(variant.sampleRate/1000,1)} kHz</p></header><audio controls preload="none" src="${esc(mediaUrl(variant.audio,base))}" aria-label="Écouter ${esc(clip.label)} : ${esc(variant.label)}"><a href="${esc(mediaUrl(variant.audio,base))}">Télécharger l’extrait WAV</a></audio><p class="lab-transform">${esc(variant.description)}</p>${clip.transcript?`<details class="lab-transcript"><summary>Paroles de l’original</summary><p lang="en">${esc(clip.transcript)}</p></details>`:''}<figure><a href="${esc(mediaUrl(figure,base))}" target="_blank" rel="noopener noreferrer" aria-label="Agrandir ${esc(DISPLAY_NAMES[display])} : ${esc(clip.label)}"><img src="${esc(mediaUrl(figure,base))}" alt="${esc(DISPLAY_NAMES[display])} calculé sur ${esc(clip.label)}, version ${esc(variant.label)}. ${esc(figureReading(catalog,display))}" loading="lazy" decoding="async"><span class="lab-enlarge">Agrandir l’image ↗</span></a><figcaption>${esc(figureReading(catalog,display))} <span>Agrandir en cliquant sur l’image.</span></figcaption></figure>${metrics(variant,original)}${credit(source)}</article>`;
  }).join('');
}
export function renderAudioLab(block,catalog,serial,base='./'){
  const options=labOptions(block,catalog),spec=LAB_VIEWS[block.view];
  if(!options.length)return '<p class="notice">Les extraits sont momentanément indisponibles.</p>';
  const display=spec.display;
  return `<section class="audio-lab" data-audio-lab="${serial}"><header><p class="eyebrow">LES MÊMES ENREGISTREMENTS, À VOIR ET À ÉCOUTER</p><h3>${esc(block.title)}</h3><p>${esc(block.introduction)}</p></header><div class="lab-controls"><label for="lab-version-${serial}">Version des deux extraits<select id="lab-version-${serial}" data-lab-version>${options.map(id=>`<option value="${id}">${esc(catalog.clips[0].variants.find(v=>v.id===id).label)}</option>`).join('')}</select></label><label for="lab-display-${serial}">Représentation<select id="lab-display-${serial}" data-lab-display>${Object.entries(DISPLAY_NAMES).map(([key,name])=>`<option value="${key}" ${key===display?'selected':''}>${esc(name)}</option>`).join('')}</select></label><label class="lab-volume" for="lab-volume-${serial}">Volume d’écoute commun<input id="lab-volume-${serial}" data-lab-volume type="range" min="0" max="1" step="0.05" value="0.5"></label></div><p class="lab-listening-note">La lecture démarre uniquement avec ▶. Gardez le même volume pour comparer les versions ; les niveaux des fichiers ne sont pas égalisés automatiquement.</p><div class="lab-display">${labDisplay(block,catalog,options[0],display,base)}</div><div class="lab-observations"><h4>Ce qu’il faut regarder et écouter</h4><ol>${block.observations.map(item=>`<li>${esc(item)}</li>`).join('')}</ol><p><strong>Ce que l’on peut conclure.</strong> ${esc(block.conclusion)}</p></div><details class="lab-protocol"><summary>Origine des fichiers et paramètres des images</summary><p>${esc(catalog.measurementConvention??'Les mesures sont calculées après export des fichiers WAV.')}</p><p>${esc(catalog.displayConvention??'Les références et les axes restent fixes entre versions comparables.')}</p><a href="${esc(mediaUrl('media/audio-lab.json',base))}" target="_blank" rel="noopener noreferrer">Consulter les paramètres et les mesures ↗</a></details></section>`;
}
export function attachAudioLabs(root,blocks,catalog,base='./'){
  const labs=blocks.filter(block=>block.type==='audio-lab');
  root.querySelectorAll('[data-audio-lab]').forEach((section,index)=>{
    const block=labs[index],version=section.querySelector('[data-lab-version]'),display=section.querySelector('[data-lab-display]'),volume=section.querySelector('[data-lab-volume]');
    const applyVolume=()=>section.querySelectorAll('audio').forEach(audio=>{audio.volume=Number(volume.value);});
    const update=()=>{
      section.querySelectorAll('audio').forEach(audio=>audio.pause());
      section.querySelector('.lab-display').innerHTML=labDisplay(block,catalog,version.value,display.value,base);
      applyVolume();
    };
    version.addEventListener('change',update);
    display.addEventListener('change',()=>{
      // Changing the representation leaves the audio element and playback untouched.
      section.querySelectorAll('.lab-clip').forEach((card,clipIndex)=>{
        const clip=catalog.clips[clipIndex],variant=clip.variants.find(item=>item.id===version.value);
        const figure=card.querySelector('figure'),src=mediaUrl(variant.figures[display.value],base);
        figure.querySelector('a').href=src;
        figure.querySelector('a').setAttribute('aria-label',`Agrandir ${DISPLAY_NAMES[display.value]} : ${clip.label}`);
        const img=figure.querySelector('img');img.src=src;img.alt=`${DISPLAY_NAMES[display.value]} calculé sur ${clip.label}, version ${variant.label}. ${figureReading(catalog,display.value)}`;
        const caption=figure.querySelector('figcaption');caption.textContent=`${figureReading(catalog,display.value)} Agrandir en cliquant sur l’image.`;
      });
    });
    volume.addEventListener('input',applyVolume);applyVolume();
  });
}

export function renderAnalysisImage(block,catalog,base='./'){
  const asset=catalog.figures?.[block.assetId];
  if(!asset)return '<p class="notice">Cette analyse est momentanément indisponible.</p>';
  const illustrated={...asset,id:block.assetId,credit:{author:asset.author??'Analyse calculée pour le cours',title:'Paramètres, mesures et sources audio',url:'https://github.com/RadioCodeur/quiz/blob/main/scripts/build-audio-media.py',license:asset.license??'CC BY 4.0',licenseUrl:asset.licenseUrl??'https://creativecommons.org/licenses/by/4.0/',changes:'Figure calculée sur les extraits documentés dans le laboratoire ; les sources audio restent créditées dans celui-ci.'}};
  const usedSources=catalog.sources.filter(source=>!asset.sourceIds||asset.sourceIds.includes(source.id));
  const credits=usedSources.length?`<details class="lab-protocol"><summary>Enregistrements utilisés dans cette figure</summary>${usedSources.map(credit).join('')}</details>`:'';
  return renderIllustration(block,{images:[illustrated]},base).replace('</figcaption>',`${credits}</figcaption>`);
}
