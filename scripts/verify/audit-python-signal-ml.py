"""Execute the Python/Signal/Audio-ML learning examples independently on CPU.

Default: read the delivered course JSON. During authoring, --fragment points to
the proposed course fragment. Real audio inputs are copied to the temporary
working directory, exactly as a learner downloads them next to their script.
"""
import argparse
import contextlib
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import shutil
import tempfile
import time

os.environ.setdefault('NUMBA_DISABLE_JIT','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('MKL_NUM_THREADS','1')
ROOT=Path(__file__).resolve().parents[2]

def check(id,block,env):
    import numpy as np
    import torch
    if id=='tableaux-et-indexation':
        if 'Y'in env:assert env['Y'].tolist()==[[2,6],[14,18],[26,30],[38,42]]and env['Y'].shape==(4,2)
        if 'fin'in env:assert env['premier'].shape==(4,)and env['une_ligne'].shape==(1,4)and env['fin'].tolist()==[[-.5,.5],[0.,1.]]
    elif id=='references-et-copies':
        assert env['signal'].tolist()==[-.5,.5,0.,.5]
        assert np.shares_memory(env['signal'],env['vue'])and not np.shares_memory(env['signal'],env['copie'])
    elif id=='reduire-les-bons-axes':
        assert env['carres'].tolist()==[[.25,.25,.25,.25],[0,0,0,1]]
        assert env['rms'].tolist()==[.5,.5]and env['cretes'].tolist()==[1,2]
    elif id=='broadcasting-et-algebre':
        if 'scores'in env:assert env['scores'].tolist()==[[2],[3]]and env['contributions'].tolist()==[[1,1],[1,2]]
        if 'dist2'in env:assert env['dist2'].tolist()==[[0],[1]]and env['ecarts'].shape==(2,1,2)
    elif id=='standardiser-et-preserver-precision':assert env['Z'].tolist()==[[0,-1],[0,1]]
    elif id=='fonctions-et-arguments':assert env['z'].tolist()==[[0,1]]
    elif id=='echantillons-duree-canaux':
        assert env['sr']==16000 and env['y'].shape==(64000,)and env['duree']==4 and env['premiere_demi_seconde'].shape==(8000,)
    elif id=='nyquist-repliement-reechantillonnage':assert env['x'].shape==(192000,)and env['y'].shape==(64000,)and len(env['x'])/env['sr']==len(env['y'])/env['sr_y']==4
    elif id=='amplitude-puissance-decibels':
        assert abs(env['peak']-.8021240234375)<1e-12 and abs(env['rms']-.12074498188527522)<1e-12
        assert abs(env['mean_square']-env['rms']**2)<1e-14
    elif id=='fourier-coefficients-frequences':assert np.allclose(env['modules'],[0,0,4,0,0])and env['f'].tolist()==[0,1000,2000,3000,4000]
    elif id=='stft-fenetres-hop-trames':assert env['D'].shape==(201,98)and env['portion_0'].shape==env['portion_1'].shape==(400,)
    elif id=='resolution-fuite-zero-padding':assert env['short'].shape==(512,)and env['long'].shape==(2048,)and env['spectrum_padded'].shape==env['spectrum_long'].shape==(1025,)
    elif id=='mel-representation-compressee':
        assert env['D'].shape==(201,98)and env['weights'].shape==(64,201)and env['mel'].shape==(64,98)
        assert np.allclose(env['mel'],env['mel_brut']/env['fenetre'].sum()**2)
        assert env['mel_db'].min()>=-100.000001
    elif id=='phase-canaux-annulations':assert env['mono'].tolist()==[0,0,0,0]
    elif id=='reconstruction-streaming-limites':
        assert env['D'].shape==(257,501)and env['y_hat'].shape==env['y_estimated'].shape==(64000,)
        assert env['erreur_complete']<1e-10 and env['future_context_seconds']==.032
    elif id=='tache-cibles-pertes':assert torch.allclose(env['probabilities'],torch.tensor([[.5,.75]]),atol=1e-6)
    elif id=='pretraitement-entrees-coherentes':assert env['scaled'].item()==2
    elif id=='durees-padding-masques':
        assert env['mask_features'].shape==(1,4,1)and env['somme'].tolist()==[[6]]and env['compte'].tolist()==[[2]]and env['pooled'].tolist()==[[3]]
    elif id=='embeddings-transfert-domaines':
        assert env['encoder_unchanged']and env['head_changed']
        assert env['embeddings'].shape==(3,512)and env['logits'].shape==(3,2)
    elif id=='architectures-axes-contexte':assert env['h'].shape==(8,16,15996)and env['z'].shape==(8,8,62,98)
    elif id=='annotations-faibles-agregation':assert abs(env['mean_score'].item()-1.84/6)<1e-6 and abs(env['max_score'].item()-.9)<1e-6
    elif id=='augmentations-cibles-validation':assert len(env['y'])==160000 and len(env['fast'])==128000 and len(env['up'])==len(env['note'])==16000 and env['new_bpm']==125 and env['new_midi']==62
    elif id=='masquage-mixup-representations':assert env['x_mix'].tolist()==[[4,5],[6,7]]and env['y_mix'].tolist()==[.25,.75]
    elif id=='similarites-contraste-attention':
        if 'summary'in env:assert abs(env['summary'].item()-4)<1e-6 and env['summary_valid'].item()==2
        else:assert env['y'].shape==(2,3,8)and torch.equal(env['weights'][0,:,2],torch.zeros(3))
    elif id=='transformer-complet':assert env['ecart_causal']==0 and env['ecart_libre']>0

def snapshot(env):
    import numpy as np
    import torch
    result={}
    for name,value in env.items():
        if isinstance(value,(np.ndarray,torch.Tensor)):
            tensor=value.detach().cpu()if isinstance(value,torch.Tensor)else value
            result[name]={'shape':list(tensor.shape),'dtype':str(tensor.dtype)}
            if tensor.size if isinstance(tensor,np.ndarray)else tensor.numel():
                count=tensor.size if isinstance(tensor,np.ndarray)else tensor.numel()
                if count<=24:result[name]['values']=safe(tensor.tolist())
        elif isinstance(value,(bool,int,float,str))and not name.startswith('__'):
            if not isinstance(value,float)or math.isfinite(value):result[name]=value
    return result

def safe(value):
    if isinstance(value,complex):return {'real':value.real,'imag':value.imag}
    if isinstance(value,float)and not math.isfinite(value):return str(value)
    if isinstance(value,list):return [safe(item)for item in value]
    return value

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fragment');parser.add_argument('--output');args=parser.parse_args()
    import numpy as np
    import torch
    torch.set_num_threads(1)
    if args.fragment:courses=json.loads((ROOT/args.fragment).read_text(encoding='utf-8'))['courses']
    else:courses=[json.loads((ROOT/'public/courses'/f'{theme}.json').read_text(encoding='utf-8'))for theme in ['python-scientifique','audio-signal','audio-ml']]
    report={'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__,'device':'cpu','cases':[],'claims':'No pretrained model quality is measured. Standalone examples define every Python object; audio inputs are declared resources.'}
    for course in courses:
        for chapter in course['chapters']:
            for index,block in enumerate(chapter['blocks']):
                if not block.get('code')or block.get('language','python')!='python':continue
                cases=[('demonstration',block['code'])]
                if block.get('variant'):
                    assert chapter['id']=='similarite-cosinus-et-contraste'
                    cases.append(('variant',block['code'].replace('b = np.array([0.6, 0.8])','b = 2 * np.array([0.6, 0.8])')))
                for role,code in cases:
                    started=time.perf_counter();env={};stdout=io.StringIO()
                    old=Path.cwd()
                    with tempfile.TemporaryDirectory(prefix='quiz-audit-audio-')as folder:
                        for resource in block.get('resources',[]):shutil.copyfile(ROOT/'public'/resource['path'],Path(folder)/Path(resource['path']).name)
                        os.chdir(folder)
                        try:
                            torch.manual_seed(17);np.random.seed(0)
                            with contextlib.redirect_stdout(stdout):exec(compile(code,chapter['id'],'exec'),env)
                            check(chapter['id'],block,env)
                        finally:os.chdir(old)
                    if block['type']=='first-example':
                        expected=block['variant']['output']if role=='variant'else block['output']
                        assert stdout.getvalue().strip()==expected.strip(),(chapter['id'],stdout.getvalue(),expected)
                    record={'themeId':course['themeId'],'chapterId':chapter['id'],'blockIndex':index,'role':role,'sourceSha256':hashlib.sha256(code.encode()).hexdigest(),'stdout':stdout.getvalue(),'seconds':round(time.perf_counter()-started,6),'values':snapshot(env)}
                    report['cases'].append(record)
                    print(chapter['id'],role,'OK',flush=True)
    report['caseCount']=len(report['cases'])
    target=ROOT/(args.output or 'scripts/verify/audit-python-signal-ml-results.json')
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('Executed',report['caseCount'],'cases on CPU.')
if __name__=='__main__':main()
