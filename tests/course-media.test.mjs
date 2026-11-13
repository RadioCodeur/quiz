import test from 'node:test';
import assert from 'node:assert/strict';
import {renderAudioLab,renderIllustration,mediaUrl,labOptions} from '../src/course-media.js';
import {readMedia,validateMedia,wavMeasures} from '../scripts/validate-media.mjs';
import {readCourses} from '../scripts/validate-courses.mjs';

test('les médias locaux, licences et mesures correspondent aux fichiers PCM réellement livrés',async()=>{
  const stats=await validateMedia(await readMedia(),await readCourses());
  assert.ok(stats.audioFiles>=12&&stats.externalIllustrations>=5);
});
test('les chemins média conservent le sous-chemin du site et refusent les échappements',()=>{
  assert.equal(mediaUrl('media/audio/voice-original.wav','/quiz/'),'/quiz/media/audio/voice-original.wav');
  for(const path of ['https://external.test/a.wav','../secret','media/../secret','media/x"onerror=1'])assert.throws(()=>mediaUrl(path));
});
test('une illustration externe reste expliquée et attribuée sans interpréter son texte comme du HTML',()=>{
  const source={id:'speech',src:'media/references/speech.png',title:'Un son <réel>',alt:'Axes < et >',caption:'Une carte <script>',reading:['Temps et fréquence','Couleur et référence'],credit:{author:'Auteur & lecteur',title:'Source',url:'https://example.org/image',license:'CC BY 4.0',licenseUrl:'https://creativecommons.org/licenses/by/4.0/',changes:'Sans modification'}};
  const rendered=renderIllustration({assetId:'speech'},{images:[source]},'/quiz/');
  assert.ok(rendered.includes('/quiz/media/references/speech.png'));
  assert.ok(rendered.includes('Auteur &amp; lecteur')&&rendered.includes('Une carte &lt;script&gt;'));
  assert.ok(rendered.includes('Comment la lire')&&rendered.includes('Sans modification'));
  assert.ok(!rendered.includes('<script>'));
});
test('le laboratoire fournit une écoute volontaire, deux fichiers identifiés et des mesures repliables',async()=>{
  const {audio}=await readMedia();
  const block={view:'level',title:'Comparer',introduction:'Mêmes fichiers',observations:['Écouter','Regarder'],conclusion:'Conclure'};
  const options=labOptions(block,audio);assert.ok(options.includes('rms-matched')&&options.includes('quiet'));
  const rendered=renderAudioLab(block,audio,'test','/quiz/');
  assert.equal((rendered.match(/<audio /g)??[]).length,2);
  assert.ok(rendered.includes('preload="none"')&&!rendered.includes('autoplay'));
  assert.ok(rendered.includes('Volume d’écoute commun')&&rendered.includes('RMS, réf. 1'));
  assert.ok(rendered.includes('/quiz/media/audio/voice-original.wav'));
});
test('le lecteur PCM traite correctement le signe et la référence numérique 1',()=>{
  const b=Buffer.alloc(48);b.write('RIFF',0);b.writeUInt32LE(40,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(2,24);b.writeUInt32LE(4,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(4,40);b.writeInt16LE(-16384,44);b.writeInt16LE(16384,46);
  const m=wavMeasures(b);assert.equal(m.duration,1);assert.equal(m.rms,.5);assert.equal(m.meanSquare,.25);assert.ok(Math.abs(m.rmsDbfs+6.020599913)<1e-8);assert.equal(m.crestDb,0);
});
