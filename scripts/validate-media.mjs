import assert from 'node:assert/strict';
import {readFile,stat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {readCourses} from './validate-courses.mjs';
import {LAB_VIEWS,mediaUrl,labOptions} from '../src/course-media.js';

export async function readMedia(){
  const [audio,illustrations]=await Promise.all(['audio-lab','illustrations'].map(async name=>JSON.parse(await readFile(new URL(`../public/media/${name}.json`,import.meta.url),'utf8'))));
  return {audio,illustrations};
}
export function wavMeasures(buffer){
  assert.equal(buffer.toString('ascii',0,4),'RIFF');assert.equal(buffer.toString('ascii',8,12),'WAVE');
  let offset=12,format,data;
  while(offset+8<=buffer.length){
    const type=buffer.toString('ascii',offset,offset+4),size=buffer.readUInt32LE(offset+4),start=offset+8;
    if(type==='fmt ')format={encoding:buffer.readUInt16LE(start),channels:buffer.readUInt16LE(start+2),sampleRate:buffer.readUInt32LE(start+4),bits:buffer.readUInt16LE(start+14)};
    if(type==='data')data=buffer.subarray(start,start+size);
    offset=start+size+(size%2);
  }
  assert.ok(format&&data);assert.equal(format.encoding,1,'PCM linéaire');assert.equal(format.channels,1,'mono');assert.equal(format.bits,16,'PCM16');
  let peak=0,squares=0;
  for(let i=0;i<data.length;i+=2){const value=data.readInt16LE(i)/32768;peak=Math.max(peak,Math.abs(value));squares+=value*value;}
  const meanSquare=squares/(data.length/2),rms=Math.sqrt(meanSquare);
  return {...format,duration:data.length/2/format.sampleRate,peak,rms,meanSquare,peakDbfs:peak?20*Math.log10(peak):null,rmsDbfs:rms?20*Math.log10(rms):null,crestDb:rms?20*Math.log10(peak/rms):null};
}
const url=value=>assert.equal(new URL(value).protocol,'https:');
export async function validateMedia({audio,illustrations},courses){
  const paths=new Set();
  async function asset(path,hash){
    mediaUrl(path);paths.add(path);
    const file=new URL(`../public/${path}`,import.meta.url);
    assert.ok((await stat(file)).size>0,`Média non vide : ${path}`);
    if(hash)assert.equal(createHash('sha256').update(await readFile(file)).digest('hex'),hash,`Empreinte : ${path}`);
    return file;
  }
  for(const source of audio.sources){assert.ok(source.id&&source.title&&source.author&&source.license&&source.changes);url(source.url);url(source.licenseUrl);url(source.downloadUrl);}
  assert.deepEqual(new Set(audio.clips.map(clip=>clip.id)),new Set(['voice','percussion']));
  let audioFiles=0,labBlocks=0,imageBlocks=0;
  for(const clip of audio.clips){
    assert.ok(audio.sources.some(source=>source.id===clip.sourceId));
    assert.equal(new Set(clip.variants.map(item=>item.id)).size,clip.variants.length);
    for(const variant of clip.variants){
      const file=await asset(variant.audio,variant.sha256),measured=wavMeasures(await readFile(file));audioFiles++;
      assert.equal(measured.sampleRate,variant.sampleRate);assert.ok(Math.abs(measured.duration-variant.duration)<1e-6);
      assert.ok(variant.description&&variant.label);
      for(const key of ['peak','rms','meanSquare','peakDbfs','rmsDbfs','crestDb']){
        const actual=measured[key],declared=variant.metrics[key];
        if(actual===null)assert.equal(declared,null,`${clip.id}/${variant.id}/${key}`);
        else assert.ok(Number.isFinite(declared)&&Math.abs(actual-declared)<1e-6,`Mesure ${clip.id}/${variant.id}/${key}: ${actual} ≠ ${declared}`);
      }
      for(const key of ['waveform','spectrogram','mel'])await asset(variant.figures[key]);
    }
    const original=clip.variants.find(v=>v.id==='original'),quiet=clip.variants.find(v=>v.id==='quiet');
    assert.ok(Math.abs((quiet.metrics.rmsDbfs-original.metrics.rmsDbfs)+6.020599913)<0.003,'Gain 0.5 : écart de −6.02 dB');
    assert.ok(Math.abs(clip.variants.find(v=>v.id==='resampled').duration-original.duration)<1e-6,'Rééchantillonnage conserve durée');
    const matched=clip.variants.find(v=>v.id==='rms-matched');if(matched)assert.ok(Math.abs(matched.metrics.rms-.08)<.00004,'RMS commun de .08');
  }
  for(const [id,figure] of Object.entries(audio.figures??{})){
    assert.ok(figure.title&&figure.alt&&figure.caption&&figure.reading?.length>=2,`Analyse documentée : ${id}`);await asset(figure.src);
  }
  assert.equal(new Set(illustrations.images.map(image=>image.id)).size,illustrations.images.length);
  for(const image of illustrations.images){
    assert.ok(image.title&&image.alt&&image.caption&&image.reading?.length>=2);
    const source=image.credit;assert.ok(source.author&&source.title&&source.license&&source.changes);url(source.url);url(source.licenseUrl);
    await asset(image.src,image.sha256);
  }
  for(const course of courses)for(const chapter of course.chapters)for(const block of chapter.blocks){
    if(block.type==='audio-lab'){
      labBlocks++;assert.ok(LAB_VIEWS[block.view]&&labOptions(block,audio).length>0);assert.ok(block.title&&block.introduction&&block.conclusion&&block.observations?.length>=2);
    }
    if(block.type==='illustration'){imageBlocks++;assert.ok(illustrations.images.some(item=>item.id===block.assetId),`Image référencée : ${block.assetId}`);}
    if(block.type==='analysis-image'){imageBlocks++;assert.ok(audio.figures?.[block.assetId],`Analyse référencée : ${block.assetId}`);}
  }
  assert.ok(labBlocks>=6&&imageBlocks>=5,'Images et écoutes effectivement intégrées aux cours');
  return {audioFiles,localAssets:paths.size,externalIllustrations:illustrations.images.length,labBlocks,imageBlocks};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)console.log(JSON.stringify(await validateMedia(await readMedia(),await readCourses()),null,2));
