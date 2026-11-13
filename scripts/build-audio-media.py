"""Build the audible course examples and plots from openly licensed recordings.

Run: python scripts/build-audio-media.py
Verify the delivered WAVs without rebuilding: python scripts/build-audio-media.py --verify
Dependencies: numpy, scipy, soundfile, matplotlib, librosa (not required by the website).
All metrics and plotted arrays are read back from the exported PCM-16 WAVs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess

os.environ.setdefault('NUMBA_DISABLE_JIT', '1')
os.environ.setdefault('MPLBACKEND', 'Agg')
import numpy as np
import scipy.signal as signal
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'public' / 'media'
AUDIO = MEDIA / 'audio'
SOURCES = AUDIO / 'sources'
FIGURES = MEDIA / 'figures'
SR = 48000
DURATION = 4.0
COLORS = ['#245446', '#ae6844']
SOURCE_DATA = [
    dict(id='libri-voice', title='The Ashiel Mystery — extrait lu',
         author='Marion Bryce (texte), Garth Comira (lecture) ; corpus LibriSpeech',
         url='https://www.openslr.org/12/', license='CC BY 4.0',
         licenseUrl='https://creativecommons.org/licenses/by/4.0/',
         downloadUrl='https://raw.githubusercontent.com/librosa/data/main/audio/5703-47212-0000.hq.ogg',
         metadataUrl='https://github.com/librosa/data/blob/main/audio/5703-47212-0000.toml',
         localFile='media/audio/sources/voice-source.ogg',
         licenseFile='media/audio/sources/voice-license.txt', cropStart=0.0,
         changes='Quatre premières secondes, décodage mono puis interpolation de 16 à 48 kHz sans normalisation de niveau. Dérivés décrits individuellement. La bande de la source reste limitée par sa cadence de 16 kHz.'),
    dict(id='librosa-snare', title='Accelerating snare drum — montage de caisse claire',
         author='Brian McFee (montage), sakebeats (enregistrement du sample)',
         url='https://github.com/librosa/data/blob/main/audio/snare-accelerate.toml',
         license='CC BY 4.0', licenseUrl='https://creativecommons.org/licenses/by/4.0/',
         downloadUrl='https://raw.githubusercontent.com/librosa/data/main/audio/snare-accelerate.ogg',
         originalSampleUrl='https://freesound.org/people/sakebeats/sounds/176345/',
         originalSampleLicense='CC0',
         metadataUrl='https://github.com/librosa/data/blob/main/audio/snare-accelerate.txt',
         localFile='media/audio/sources/percussion-source.ogg',
         licenseFile='media/audio/sources/percussion-license.txt', cropStart=8.0,
         changes='Secondes 8 à 12 du montage accéléré de frappes enregistrées ; décodage mono puis interpolation de 22,05 à 48 kHz sans normalisation de niveau. Ce n’est pas une nouvelle prise jouée en continu. Dérivés décrits individuellement.'),
]


def db(value, coefficient=20):
    return None if value == 0 else float(coefficient * np.log10(value))


def metrics(x):
    peak = float(np.max(np.abs(x)))
    mean_square = float(np.mean(x * x))
    rms = math.sqrt(mean_square)
    return dict(peak=peak, rms=rms, meanSquare=mean_square,
                peakDbfs=db(peak), rmsDbfs=db(rms),
                crestDb=None if rms == 0 else db(peak / rms),
                digitalFullScaleFraction=float(np.mean(np.abs(x) >= 32767 / 32768)))


def relative(path):
    return path.relative_to(ROOT / 'public').as_posix()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_sources():
    SOURCES.mkdir(parents=True, exist_ok=True)
    for source in SOURCE_DATA:
        path = ROOT / 'public' / source['localFile']
        if not path.exists() or path.stat().st_size < 1024:
            subprocess.run(['curl.exe' if os.name == 'nt' else 'curl', '-sS', '--fail',
                            '--max-time', '45', source['downloadUrl'], '-o', str(path)], check=True)
        source['sha256'] = sha256(path)
        source['bytes'] = path.stat().st_size
        license_path=ROOT/'public'/source['licenseFile']
        if not license_path.exists():
            license_url=source['downloadUrl'].replace('.hq.ogg','.txt').replace('.ogg','.txt')
            subprocess.run(['curl.exe' if os.name == 'nt' else 'curl','-sS','--fail','--max-time','45',license_url,'-o',str(license_path)],check=True)


def export_audio(clip_id, variant_id, x, sr, label, description, parameters):
    path = AUDIO / f'{clip_id}-{variant_id}.wav'
    assert np.isfinite(x).all()
    assert np.max(np.abs(x)) <= 1
    sf.write(path, x, sr, subtype='PCM_16')
    exported, actual_sr = sf.read(path, dtype='float64')
    assert actual_sr == sr
    return dict(id=variant_id, label=label, audio=relative(path),
                sampleRate=sr, duration=len(exported) / sr, description=description,
                metrics=metrics(exported), figures={}, parameters=parameters,
                sha256=sha256(path), bytes=path.stat().st_size), exported


def stft(x, sr, window_ms=25):
    import librosa
    n_fft = int(round(sr * window_ms / 1000))
    hop = int(round(sr * 0.010))
    # Hann periodic window; raw STFT divided by its sum. This is not a PSD.
    window = signal.windows.hann(n_fft, sym=False)
    D = librosa.stft(x, n_fft=n_fft, hop_length=hop, win_length=n_fft,
                     window=window, center=True, pad_mode='constant')
    return D, n_fft, hop, window


def spectral(x, sr, window_ms=25, with_mel=True):
    import librosa
    D, n_fft, hop, window = stft(x, sr, window_ms)
    power = np.abs(D / window.sum()) ** 2
    filters = librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=64,
                                  fmin=0, fmax=8000, htk=False, norm='slaney') if with_mel else None
    mel = filters @ power if with_mel else None
    return dict(D=D, power=power, mel=mel, filters=filters, n_fft=n_fft, hop=hop,
                times=np.arange(D.shape[1]) * hop / sr,
                frequencies=np.fft.rfftfreq(n_fft, 1 / sr))


def level_db(power):
    # One fixed reference for ALL recordings and variants. No ref=max scaling.
    return 10 * np.log10(np.maximum(power, 1e-10))


def setup_plots():
    import matplotlib as mpl
    mpl.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                         'axes.titlesize': 15, 'axes.labelsize': 12,
                         'figure.facecolor': '#f7faf1', 'axes.facecolor': '#fcfdf9',
                         'axes.edgecolor': '#9aac8d', 'axes.labelcolor': '#31543d',
                         'text.color': '#244334', 'xtick.color': '#53664b',
                         'ytick.color': '#53664b', 'grid.color': '#d6e0cd'})


def save(fig, name):
    from matplotlib import pyplot as plt
    path = FIGURES / name
    fig.savefig(path, dpi=125, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return relative(path)


def plot_variants(clip, arrays):
    from matplotlib import pyplot as plt
    import librosa.display
    for variant in clip['variants']:
        x = arrays[variant['id']]
        sr = variant['sampleRate']
        prefix = f"{clip['id']}-{variant['id']}"
        data = spectral(x, sr)
        variant['parameters'].update(window='Hann périodique', windowMs=25, hopMs=10,
                                     nFft=data['n_fft'], hopLength=data['hop'], center=True,
                                     stftShape=list(data['D'].shape),
                                     stftScale='P = abs(STFT(x) / sum(fenetre)) ** 2 ; affichage 10 log10(max(P,1e-10)/1). Référence spectrale 1 commune, non calibrée en W ni en dB SPL.',
                                     melScale='64 filtres Slaney normalisés en aire, 0–8000 Hz, appliqués à P ; affichage 10 log10(max(M,1e-10)/1), référence 1 fixe. Ce n’est pas le dBFS du RMS.',
                                     colorLimitsDb=[-100, 0], spectrogramFrequencyLimitHz=12000)
        fig, ax = plt.subplots(figsize=(10.5, 3.3), layout='constrained')
        stride = max(1, len(x) // 4000)
        # Preserve extrema in each display bin, not just one sample per bin.
        length = len(x) - len(x) % stride
        blocks = x[:length].reshape(-1, stride)
        times = (np.arange(len(blocks)) * stride + stride / 2) / sr
        ax.fill_between(times, blocks.min(axis=1), blocks.max(axis=1), color=COLORS[0], alpha=.65)
        ax.set(xlim=(0, DURATION), ylim=(-1.02, 1.02), xlabel='Temps (s)',
               ylabel='Amplitude numérique', title=f"{clip['label']} — {variant['label']}")
        ax.grid(alpha=.5)
        variant['figures']['waveform'] = save(fig, prefix + '-waveform.png')

        fig, ax = plt.subplots(figsize=(10.5, 4.6), layout='constrained')
        img = ax.pcolormesh(data['times'], data['frequencies'], level_db(data['power']),
                            vmin=-100, vmax=0, cmap='magma', shading='nearest', rasterized=True)
        ax.set(xlim=(0, DURATION), ylim=(0, 12000), xlabel='Temps (s)',
               ylabel='Fréquence (Hz)', title=f"{clip['label']} — STFT, fenêtre 25 ms")
        if sr / 2 < 12000:
            ax.axhspan(sr / 2, 12000, facecolor='#dfe4d8', hatch='///', edgecolor='#a0ac95')
            ax.text(2, 10200, 'Hors de la bande représentable à 16 kHz', ha='center', fontsize=10)
        fig.colorbar(img, ax=ax, label='10 log10(P / 1), dB relatifs ; réf. fixe')
        variant['figures']['spectrogram'] = save(fig, prefix + '-stft.png')

        fig, ax = plt.subplots(figsize=(10.5, 4.6), layout='constrained')
        img = librosa.display.specshow(level_db(data['mel']), sr=sr,
                                       hop_length=data['hop'], x_axis='time', y_axis='mel',
                                       fmin=0, fmax=8000, htk=False, ax=ax,
                                       vmin=-100, vmax=0, cmap='magma')
        ax.set(xlim=(0, DURATION), ylim=(0,8000), yticks=[0,500,1000,2000,4000,8000],
               yticklabels=['0','500','1000','2000','4000','8000'], xlabel='Temps (s)', ylabel='Fréquence (Hz), échelle mel',
               title=f"{clip['label']} — 64 bandes mel")
        fig.colorbar(img, ax=ax, label='10 log10(M / 1), dB relatifs ; réf. fixe')
        variant['figures']['mel'] = save(fig, prefix + '-mel.png')


def extra_figures(clips, audio_arrays):
    from matplotlib import pyplot as plt
    import librosa
    output = {}
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True, sharey=True, layout='constrained')
    for row, clip in enumerate(clips):
        x = audio_arrays[clip['id']]['original']
        for col, window_ms in enumerate([10, 80]):
            d = spectral(x, SR, window_ms, with_mel=False)
            ax = axes[row, col]
            img = ax.pcolormesh(d['times'], d['frequencies'], level_db(d['power']),
                               vmin=-100, vmax=0, cmap='magma', shading='nearest', rasterized=True)
            ax.set(xlim=(0, DURATION), ylim=(0, 8000), title=f"{clip['label']} : {window_ms} ms ({1000/window_ms:.1f} Hz/bin)",
                   xlabel='Temps (s)', ylabel='Fréquence (Hz)')
    fig.colorbar(img, ax=axes, label='Puissance STFT relative (dB, réf.1 commune)', shrink=.9)
    output['stft-windows'] = dict(src=save(fig, 'stft-window-comparison.png'),
                                title='Même son : fenêtres courtes ou longues',
                                caption='Hann 10 ms et 80 ms, hop 10 ms, même référence de couleur. La précision en temps et la grille fréquentielle changent ; une fenêtre longue peut étaler une attaque. La résolution physique dépend aussi de la largeur du lobe de la fenêtre, pas seulement du pas des bins.')

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), layout='constrained')
    x = audio_arrays['voice']['original']
    n = int(.025 * SR)
    start = int(1.0 * SR)
    segment = x[start:start+n]
    window = signal.windows.hann(n, sym=False)
    t = np.arange(n) / SR * 1000
    axes[0].plot(t, segment, color=COLORS[0], lw=1)
    axes[0].set(title='1. Prendre 25 ms dans la voix réelle, à t=1 s', ylabel='Amplitude', xlabel='Temps dans la fenêtre (ms)')
    axes[1].plot(t, window, color=COLORS[1]);axes[1].set(title='2. Pondérer avec la fenêtre de Hann', ylabel='Poids', xlabel='Temps dans la fenêtre (ms)')
    axes[2].plot(t, segment*window, color=COLORS[0], lw=1)
    axes[2].set(title='3. Transformer cette portion pondérée, puis décaler de 10 ms', ylabel='Amplitude pondérée', xlabel='Temps dans la fenêtre (ms)')
    for ax in axes: ax.grid(alpha=.4)
    output['stft-windowing'] = dict(src=save(fig, 'stft-real-window.png'), title='Une fenêtre appliquée à la voix réelle',
                                   caption='Le signal n’est pas remplacé par un dessin idéal : ces 1200 valeurs proviennent de la référence voix à 48 kHz. Fenêtre 25 ms et déplacement 10 ms : les portions voisines se recouvrent.')

    fig, ax = plt.subplots(figsize=(10.5, 4.4), layout='constrained')
    filters = librosa.filters.mel(sr=SR, n_fft=1200, n_mels=16, fmin=0, fmax=8000, norm='slaney')
    freq = np.fft.rfftfreq(1200, 1/SR)
    for f in filters: ax.plot(freq, f, lw=1.4)
    ax.set(xlim=(0,8000), xlabel='Fréquence linéaire (Hz)', ylabel='Poids du filtre (normalisation en aire)', title='16 filtres mel pour lire le principe ; nos cartes en utilisent 64')
    ax.grid(alpha=.4)
    output['mel-filterbank'] = dict(src=save(fig,'mel-filterbank.png'), title='Comment les bandes mel regroupent les fréquences',
                                  caption='Filtres triangulaires Slaney, normalisés en aire. Ils sont plus larges dans les aigus ; la hauteur change avec cette normalisation. Le regroupement fait perdre des détails ; ce n’est pas seulement un changement d’étiquette de l’axe.')

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout='constrained')
    labels=[clip['label'] for clip in clips]
    peaks=[clip['variants'][0]['metrics']['peakDbfs'] for clip in clips]
    rmss=[clip['variants'][0]['metrics']['rmsDbfs'] for clip in clips]
    xx=np.arange(2)
    axes[0].bar(xx-.17,peaks,width=.32,label='Crête',color=COLORS[1])
    axes[0].bar(xx+.17,rmss,width=.32,label='RMS',color=COLORS[0])
    axes[0].set(xticks=xx,xticklabels=labels,ylim=(-32,0),ylabel='dBFS, référence numérique 1',title='Mesures sur les 4 secondes livrées')
    axes[0].legend()
    for x0,val in zip(xx-.17,peaks): axes[0].text(x0,val+1.5,f'{val:.1f}',ha='center',va='top',color='white',fontsize=10)
    for x0,val in zip(xx+.17,rmss): axes[0].text(x0,val+1.5,f'{val:.1f}',ha='center',va='top',color='white',fontsize=10)
    for i,clip in enumerate(clips):
        v=next(v for v in clip['variants'] if v['id']=='rms-matched')
        axes[1].scatter(v['metrics']['rmsDbfs'],v['metrics']['peakDbfs'],s=100,color=COLORS[i],label=clip['label'])
    axes[1].set(xlabel='RMS (dBFS)',ylabel='Crête (dBFS)',xlim=(-24,-20),ylim=(-10,0),title='Après réglage au même RMS : pics différents')
    axes[1].legend()
    for ax in axes:ax.grid(axis='y',alpha=.3)
    output['level-comparison']=dict(src=save(fig,'real-level-comparison.png'),title='Crête et RMS des deux enregistrements',
                                    caption='À gauche, les références sans normalisation de niveau : la voix présente ici des valeurs plus élevées, mais la percussion possède un plus grand facteur de crête. À droite, les variantes réglées au même RMS de 0,08 : le pic de la percussion est plus élevé. Ces chiffres décrivent les fichiers et leurs gains, pas le niveau acoustique des sources en dB SPL.')

    fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True,sharey=True,layout='constrained')
    for ax,clip in zip(axes,clips):
        for variant_id,color in [('original',COLORS[0]),('resampled',COLORS[1])]:
            v=next(v for v in clip['variants'] if v['id']==variant_id)
            x=audio_arrays[clip['id']][variant_id]
            ff,pp=signal.welch(x,fs=v['sampleRate'],window='hann',nperseg=int(v['sampleRate']*.04),scaling='spectrum')
            ax.plot(ff,10*np.log10(np.maximum(pp,1e-12)),color=color,lw=1.2,label=v['label'])
        ax.axvline(8000,color='#6e7a67',ls='--',label='Nyquist à 16 kHz')
        ax.set(xlim=(0,12000),ylim=(-120,-10),title=clip['label'],ylabel='Spectre Welch relatif (dB)',xlabel='Fréquence (Hz)')
        ax.legend(fontsize=9);ax.grid(alpha=.3)
    output['resampling-bandwidth']=dict(src=save(fig,'resampling-bandwidth.png'),title='Le rééchantillonnage ne crée pas de bande nouvelle',
                                        caption='La voix source était déjà à 16 kHz : l’interpolation 48 kHz ne lui ajoute aucun détail au-dessus de 8 kHz. La percussion source 22,05 kHz possède une bande plus large ; son passage à 16 kHz atténue le haut du spectre avant décimation. Welch, fenêtre 40 ms, même référence numérique 1.')
    # Real arrays, displayed as a model input: C=1 is an added model channel axis.
    mel_arrays=[spectral(audio_arrays[clip['id']]['original'], SR)['mel'] for clip in clips]
    batch=np.stack(mel_arrays)[:, None, :, :]
    assert batch.shape==(2,1,64,401)
    fig,axes=plt.subplots(1,2,figsize=(13,5),sharey=True,layout='constrained')
    for i,(ax,clip,mel) in enumerate(zip(axes,clips,mel_arrays)):
        img=ax.imshow(level_db(mel),origin='lower',aspect='auto',extent=[0,4,0,64],
                      vmin=-100,vmax=0,cmap='magma')
        ax.set(title=f"Extrait {i} : {clip['label']} · canal modèle 0",xlabel='Temps (s) ; 401 trames',ylabel='Indice de bande mel ; 64 bandes')
    fig.suptitle('Forme (2, 1, 64, 401) : 2 extraits, 1 canal modèle, 64 bandes, 401 trames',fontsize=14)
    fig.colorbar(img,ax=axes,label='Puissance mel relative (dB, réf. 1 commune)',shrink=.8)
    output['tensor-axes']=dict(src=save(fig,'real-mel-tensor-axes.png'),
                              title='Les axes d’un tenseur sur deux cartes réellement calculées',
                              caption='B choisit un extrait, C est ici un axe de canal modèle ajouté (taille 1), F les 64 bandes mel et T les 401 trames de 10 ms, avec centrage et padding. Ces deux images ne sont pas les canaux gauche et droit d’un fichier stéréo.',
                              parameters=dict(shape=list(batch.shape),hopMs=10,windowMs=25,padding='center=True',nMels=64,fmaxHz=8000))

    mel=mel_arrays[0]
    masked=mel.copy();masked[20:34,:]=0;masked[:,100:140]=0
    fig,axes=plt.subplots(1,2,figsize=(13,5),sharey=True,layout='constrained')
    for ax,values,title in zip(axes,[mel,masked],['Voix : entrée non masquée','Même entrée : bandes et temps masqués']):
        img=ax.imshow(level_db(values),origin='lower',aspect='auto',extent=[0,4,0,64],
                      vmin=-100,vmax=0,cmap='magma')
        ax.set(title=title,xlabel='Temps (s)',ylabel='Indice de bande mel')
    fig.colorbar(img,ax=axes,label='Puissance mel relative (dB, réf. 1 commune)',shrink=.8)
    output['augmentation-mask']=dict(src=save(fig,'real-mel-augmentation-mask.png'),
                                     title='Masquer une partie de l’entrée sans fabriquer un autre enregistrement',
                                     caption='Nous mettons à zéro la puissance linéaire des bandes 20 à 33 et des trames 100 à 139 (centres de trames de 1,00 à 1,39 s). Les zones affichées au plancher sont des données masquées, pas une absence mesurée dans la prise. Aucune écoute correspondante n’est prétendue : c’est une transformation de l’entrée du modèle.',
                                     parameters=dict(frequencyMask=[20,34],timeMask=[100,140],maskedValue=0,domain='mel power, before log display',audioReconstructed=False))

    for key,item in output.items():
        item.setdefault('alt',item['title']+'. '+item['caption'])
        item.setdefault('reading',[])
        item.setdefault('parameters',{})
        item.update(author='Calcul et tracé pour ce cours, à partir des enregistrements crédités',
                    license='CC BY 4.0',licenseUrl='https://creativecommons.org/licenses/by/4.0/',
                    sourceIds=([] if key=='mel-filterbank' else ['libri-voice'] if key in ['stft-windowing','augmentation-mask'] else ['libri-voice','librosa-snare']),
                    script='scripts/build-audio-media.py')
    output['stft-windows']['reading']=['Les quatre cartes utilisent les deux mêmes WAV de référence et une seule échelle de couleur.',
        'Les fenêtres de 10 ms localisent les attaques mais séparent moins les fréquences voisines.',
        'Les fenêtres de 80 ms détaillent mieux les bandes fréquentielles mais étalent davantage les événements courts.']
    output['stft-windowing']['reading']=['La première courbe est une portion de la voix enregistrée, et non une sinusoïde inventée.',
        'Le poids de Hann s’approche de zéro aux bords pour adoucir la découpe.',
        'La STFT répète le calcul spectral sur ces portions pondérées, ici avec recouvrement.']
    output['mel-filterbank']['reading']=['Chaque triangle indique le poids donné aux fréquences d’une bande.',
        'La normalisation en aire explique pourquoi les triangles larges sont moins hauts.',
        'Les cartes utilisent 64 bandes ; les 16 triangles ici servent à rendre les recouvrements lisibles.']
    output['level-comparison']['reading']=['La barre de crête est le maximum absolu ; la barre RMS résume les 4 secondes complètes, pauses comprises.',
        'L’écart entre crête et RMS donne le facteur de crête : plus grand pour la percussion de cet exemple.',
        'Une différence de dBFS entre fichiers ne révèle pas une différence de dB SPL entre les sources.']
    output['resampling-bandwidth']['reading']=['Les lignes comparent la référence interpolée à 48 kHz et sa version filtrée à 16 kHz, pas deux prises différentes.',
        'La ligne verticale à 8 kHz repère la frontière de Nyquist de la version à 16 kHz.',
        'La voix source était déjà à 16 kHz : augmenter sa cadence ne crée pas d’information nouvelle.']
    output['tensor-axes']['reading']=['B=0 et B=1 désignent deux enregistrements distincts.',
        'C=1 est une dimension ajoutée au tableau pour le réseau ; les sources sont mono.',
        'La forme (2,1,64,401) se déduit de l’empilement des cartes réelles et des paramètres STFT.']
    output['augmentation-mask']['reading']=['Le contenu de départ est la carte mel de la voix de référence.',
        'La bande horizontale et la bande verticale sont des suppressions construites, documentées dans les paramètres.',
        'On peut utiliser cette entrée pour entraîner le modèle ; elle ne constitue pas un nouveau WAV à écouter.']
    return output


def build(skip_images=False):
    import librosa
    ensure_sources()
    AUDIO.mkdir(parents=True, exist_ok=True);FIGURES.mkdir(parents=True, exist_ok=True)
    manifest=dict(version=1, generatedBy='scripts/build-audio-media.py',
                  sources=SOURCE_DATA, clips=[], figures={},
                  measurementConvention='WAV mono PCM16 relu après export. Crête=max(abs(x)), puissance numérique moyenne=mean(x**2), RMS=sqrt(puissance). dBFS(crête)=20log10(crête/1), dBFS(RMS)=20log10(RMS/1) : référence RMS1, sans décalage AES17. Pas de calibration en pascals, watts ou dB SPL.',
                  displayConvention='Écoutes sans normalisation automatique. Le curseur commun est initialisé à 0,5 et règle le volume de tous les lecteurs ; il ne change pas les mesures des fichiers. Aucune lecture automatique. Toutes les cartes STFT et mel utilisent une référence de couleur 1 fixe, jamais le maximum de chaque image.',
                  buildVersions=dict(numpy=np.__version__, librosa=librosa.__version__, soundfile=sf.__version__))
    audio_arrays={}
    for clip_id,label,source in zip(['voice','percussion'],['Voix parlée','Caisse claire'],SOURCE_DATA):
        native,native_sr=sf.read(ROOT/'public'/source['localFile'],dtype='float64')
        if native.ndim>1:native=native.mean(axis=1)
        begin=int(round(source['cropStart']*native_sr));end=begin+int(round(DURATION*native_sr))
        native=native[begin:end]
        divisor=math.gcd(native_sr,SR)
        x=signal.resample_poly(native,SR//divisor,native_sr//divisor)
        clip=dict(id=clip_id,label=label,sourceId=source['id'],nativeSampleRate=native_sr,
                  cropStart=source['cropStart'],duration=DURATION,variants=[])
        arrays={}
        def add(id,values,sr,label,description,**parameters):
            variant,readback=export_audio(clip_id,id,values,sr,label,description,parameters)
            clip['variants'].append(variant);arrays[id]=readback
            return readback
        x=add('original',x,SR,'Référence à 48 kHz (interpolée)',
              f"Extrait réel mono de 4 s ; source à {native_sr:,} Hz interpolée à 48 000 Hz. Aucun gain de normalisation. Une cadence plus haute ne recrée pas les aigus absents.".replace(',', ' '),
              nativeSampleRate=native_sr,cropStart=source['cropStart'],gain=1,resampler='scipy.signal.resample_poly, fenêtre Kaiser par défaut')
        add('quiet',x*.5,SR,'Gain ÷ 2 (−6,02 dB)',
            'Toutes les amplitudes sont divisées par 2. Le RMS et la crête baissent d’environ 6,02 dB ; la puissance moyenne est divisée par 4. Aucun ajustement automatique du lecteur.',gain=.5)
        reference_rms=math.sqrt(np.mean(x*x));gain=.08/reference_rms
        assert np.max(np.abs(x*gain))<1
        add('rms-matched',x*gain,SR,'RMS commun 0,08',
            'Gain constant choisi pour atteindre un RMS de 0,08. Les deux extraits ont ainsi presque le même RMS après quantification ; leurs pics et leurs timbres peuvent rester différents.',gain=float(gain),targetRms=.08)
        add('resampled',signal.resample_poly(x,1,3),16000,'Rééchantillonné 16 kHz',
            'Filtrage antirepliement puis calcul de trois fois moins de valeurs. Durée 4 s conservée ; aucune fréquence représentable au-dessus de 8 kHz.',up=1,down=3,resampler='scipy.signal.resample_poly, fenêtre Kaiser par défaut')
        sos=signal.butter(6,1000,fs=SR,output='sos')
        filtered=signal.sosfiltfilt(sos,x)
        add('lowpass',filtered,SR,'Passe-bas 1 kHz',
            'Filtre Butterworth ordre 6 appliqué aller-retour : forte atténuation des aigus, durée conservée. Le niveau peut changer ; il n’est pas renormalisé.',cutoffHz=1000,order=6,filter='Butterworth, sosfiltfilt aller-retour')
        add('clipped',np.clip(4*x,-.98,.98),SR,'Gain × 4 puis écrêtage',
            'Le gain × 4 aurait dépassé la pleine échelle. Nous limitons artificiellement à ±0,98 : les pics sont aplatis et des composantes nouvelles peuvent apparaître. C’est une démonstration de distorsion.',gain=4,clipThreshold=.98,preClipFraction=float(np.mean(np.abs(4*x)>.98)))
        add('polarity-inverted',-x,SR,'Polarité inversée',
            'Chaque amplitude est multipliée par −1. Écoutée seule, cette inversion conserve presque exactement RMS, crête et spectre ; le changement devient décisif lorsque des signaux se mélangent.',gain=-1)
        add('cancelled',np.zeros_like(x),SR,'Deux canaux opposés : somme nulle',
            'Démonstration construite à partir de cette prise mono : gauche=x, droite=−x, puis (gauche+droite)/2. Ce ne sont pas deux microphones réels : les canaux artificiels s’annulent exactement.',construction='(x + (-x)) / 2',artificialStereo=True)
        D,nfft,hop,window=stft(x,SR)
        rng=np.random.default_rng(20261112)
        random_phase=rng.uniform(-np.pi,np.pi,size=D.shape)
        candidate=np.abs(D)*np.exp(1j*random_phase)
        # DC and Nyquist coefficients of a real signal must be real: phases 0 or pi.
        candidate[0]=np.abs(D[0])*rng.choice([-1.,1.],size=D.shape[1])
        candidate[-1]=np.abs(D[-1])*rng.choice([-1.,1.],size=D.shape[1])
        assert np.allclose(np.abs(candidate),np.abs(D),rtol=1e-12,atol=1e-12)
        reconstructed=librosa.istft(candidate,hop_length=hop,win_length=nfft,window=window,
                                    center=True,length=len(x))
        matching_gain=reference_rms/math.sqrt(np.mean(reconstructed**2))
        reconstructed*=matching_gain
        assert np.max(np.abs(reconstructed))<1
        add('phase-random',reconstructed,SR,'Reconstruction avec phase aléatoire',
            'La cible conserve le module STFT et remplace sa phase par des angles aléatoires ; iSTFT reconstruit un signal. Le RMS est ensuite rapproché de la référence pour l’écoute. Une STFT à phase arbitraire n’est généralement pas cohérente : la STFT du WAV reconstruit n’a donc pas exactement le module cible.',seed=20261112,rmsMatchingGain=float(matching_gain),target='module STFT conservé avant projection iSTFT ; phase aléatoire',magnitudePreservedAfterReconstruction=False)
        # The phase-correct inverse provides a numerical baseline, not another audio variant.
        restored=librosa.istft(D,hop_length=hop,win_length=nfft,window=window,center=True,length=len(x))
        clip['istftRoundTripMaxError']=float(np.max(np.abs(restored-x)))
        assert clip['istftRoundTripMaxError']<1e-10
        audio_arrays[clip_id]=arrays;manifest['clips'].append(clip)
    if not skip_images:
        setup_plots()
        for clip in manifest['clips']:plot_variants(clip,audio_arrays[clip['id']])
        manifest['figures']=extra_figures(manifest['clips'],audio_arrays)
    else:
        # Metrics-only mode is useful during authoring; never publish without the figures.
        manifest['imagesPending']=True
    output=MEDIA/'audio-lab.json';output.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    verify(manifest,require_images=not skip_images)
    for clip in manifest['clips']:
        for variant in clip['variants']:
            if variant['id'] in ['original','quiet','rms-matched']:
                m=variant['metrics']
                print(clip['id'],variant['id'],json.dumps(m,ensure_ascii=True))
    print('Built',len(manifest['clips']),'clips,',sum(len(c['variants']) for c in manifest['clips']),'variants.')


def verify(manifest,require_images=True):
    total=0
    for clip in manifest['clips']:
        by_id={v['id']:v for v in clip['variants']}
        for variant in clip['variants']:
            path=ROOT/'public'/variant['audio'];x,sr=sf.read(path,dtype='float64')
            assert sr==variant['sampleRate'] and len(x)/sr==DURATION
            assert np.isfinite(x).all() and np.max(np.abs(x))<=1
            assert sha256(path)==variant['sha256']
            for name,value in metrics(x).items():
                target=variant['metrics'][name]
                assert (value is None and target is None) or abs(value-target)<1e-10,(clip['id'],variant['id'],name)
            if require_images:
                assert len(variant['figures'])==3
                for src in variant['figures'].values():assert (ROOT/'public'/src).is_file()
            total+=1
        delta=by_id['quiet']['metrics']['rmsDbfs']-by_id['original']['metrics']['rmsDbfs']
        assert abs(delta-20*np.log10(.5))<.003,delta
        assert abs(by_id['rms-matched']['metrics']['rms']-.08)<2e-5
        assert by_id['cancelled']['metrics']['rmsDbfs'] is None
        assert abs(by_id['polarity-inverted']['metrics']['rms']-by_id['original']['metrics']['rms'])<2e-5
    print('Verified',total,'PCM16 files: finite audio, exact metrics, 4 s, gain -6.02 dB, RMS matching, cancellation and assets.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');parser.add_argument('--skip-images',action='store_true')
    args=parser.parse_args()
    if args.verify:verify(json.loads((MEDIA/'audio-lab.json').read_text('utf-8')))
    else:build(args.skip_images)
