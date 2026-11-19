"""Run every Python block in the four audit-owned modules on CPU.

The website never imports this script. --fragment checks the review fragment
before integration; the default reads the delivered course files.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import platform
import time

os.environ.setdefault('NUMBA_DISABLE_JIT','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
ROOT=Path(__file__).resolve().parents[2]
THEMES=['generation-controle','evaluation-recherche','contexte-recherche','entretien']

def snapshot(value):
    import numpy as np
    import torch
    if isinstance(value,torch.Tensor):
        return {'shape':list(value.shape),'dtype':str(value.dtype),'values':value.detach().cpu().tolist()}if value.numel()<=30 else {'shape':list(value.shape),'dtype':str(value.dtype)}
    if isinstance(value,np.ndarray):return value.tolist()if value.size<=30 else {'shape':list(value.shape)}
    if isinstance(value,(str,int,float,bool,type(None))):return value
    return None

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fragment',action='store_true');args=parser.parse_args()
    import numpy as np
    import torch
    torch.set_num_threads(1)
    if args.fragment:
        courses=json.loads((ROOT/'work/audit-generation-research-oral.json').read_text(encoding='utf-8'))['courses']
    else:courses=[json.loads((ROOT/'public/courses'/f'{theme}.json').read_text(encoding='utf-8'))for theme in THEMES]
    spec=importlib.util.spec_from_file_location('existing_scaffolds',ROOT/'scripts/verify/existing-corpus.py')
    existing=importlib.util.module_from_spec(spec);spec.loader.exec_module(existing)
    report={'python':platform.python_version(),'torch':torch.__version__,'device':'cpu','threads':1,'examples':[],'numericalChecks':{},'limits':['No neural audio model is pretrained or benchmarked here.','Identity decoders and fixed predictions are labelled pedagogical fixtures.','The evaluation decisions are fabricated; bootstrap intervals do not establish real musical superiority.']}
    changed={}
    for course in courses:
        for chapter in course['chapters']:
            annex=next((b for b in chapter['blocks']if b.get('disclosure')and b.get('codeMode')=='standalone'),None)
            for index,block in enumerate(chapter['blocks']):
                code=block.get('code')
                if not code or block.get('language','python')!='python':continue
                variants=[(False,code)]
                if block.get('variant'):
                    before,after=existing.VARIANTS[chapter['id']]
                    assert before in code
                    variants.append((True,code.replace(before,after,1)))
                for variant,source in variants:
                    torch.manual_seed(0);np.random.seed(0)
                    env={'np':np,'torch':torch,'math':math}
                    context=''
                    if block.get('codeMode')=='excerpt':
                        if annex and code in annex['code']:
                            context=annex['code'].split(code,1)[0]
                        elif chapter['id']=='variabilite-et-incertitude':
                            context=annex['code'].split('sampled = rng.choice',1)[0]
                        else:context=existing.SCAFFOLDS.get(chapter['id'],'')
                        assert context,chapter['id']
                    stream=io.StringIO();started=time.perf_counter()
                    with contextlib.redirect_stdout(stream):
                        if context:exec(compile(context,'context/'+chapter['id'],'exec'),env)
                        exec(compile(source,chapter['id'],'exec'),env)
                    stdout=stream.getvalue().strip()
                    if block['type']=='first-example':
                        expected=block['variant']['output']if variant else block['output']
                        assert stdout==expected,(chapter['id'],stdout,expected)
                    values={key:result for key,value in env.items()if (result:=snapshot(value))is not None and not key.startswith('__')}
                    report['examples'].append({'themeId':course['themeId'],'chapterId':chapter['id'],'blockIndex':index,'variant':variant,'codeSha256':hashlib.sha256(source.encode()).hexdigest(),'codeMode':block.get('codeMode'),'scaffold':context,'stdout':stdout,'seconds':round(time.perf_counter()-started,6),'values':values})
                    print('OK',chapter['id'],index,'variant'if variant else '',flush=True)
                    changed[(chapter['id'],bool(block.get('disclosure')),variant)]=env
    # Checks target meanings and numerical claims, not the presence of keywords.
    rvq=changed[('codecs-neuronaux-rvq',False,False)]
    assert torch.allclose(rvq['z'],torch.tensor([[.9],[-.8]]))
    assert rvq['codes'][0].tolist()==[2,0]and rvq['codes'][1].tolist()==[1,2]
    assert abs(rvq['mse'].item()-.00625)<1e-7
    vae=changed[('vae-et-echantillonnage',True,False)]
    assert vae['z'].tolist()==[[1.]]and vae['mu'].tolist()==[[2.]]
    lora=changed[('adaptation-lora-et-petit-corpus',True,False)]
    assert lora['W0'].grad is None and bool((lora['A'].grad==0).all())and bool((lora['B'].grad!=0).any())
    assert lora['petite_activation'].shape==(1,)and lora['correction'].shape==(3,)
    diff=changed[('diffusion-et-bruit',True,False)]
    assert abs(diff['xt'].item()-.2)<1e-6 and abs(diff['loss'].item()-.04)<1e-6
    guidance=changed[('guidance-et-zones-connues',True,False)]
    assert guidance['output'].tolist()==torch.tensor([.1,.2,7.,6.]).tolist()
    altered=torch.where(torch.tensor([True,True,True,False]),guidance['observed'],guidance['generated'])
    assert altered.tolist()==torch.tensor([.1,.2,.3,6.]).tolist()
    flow=changed[('objectifs-diffusion-et-flow',False,False)]
    assert flow['point'].item()==-.25 and flow['vitesse_cible'].item()==3.
    assert (flow['z']+.5*flow['vitesse_cible']).item()==.5
    metrics=changed[('metriques-et-seuils',False,False)]
    assert metrics['precision']==.75 and metrics['recall']==.6 and metrics['balanced_accuracy']==.7
    evalcase=changed[('baselines-et-ablations',True,False)]
    scores=[int((evalcase[name]==evalcase['truth']).sum())for name in ['pred_base','pred_a','pred_b','pred_ab']]
    assert scores==[70,72,71,76]
    assert evalcase['cm'].tolist()==[[40,10],[20,30]]
    bootstrap=changed[('variabilite-et-incertitude',True,False)]
    assert len(bootstrap['recording_ids'])==len(bootstrap['sampled'])==20
    assert len(set(bootstrap['sampled']))<20
    assert math.isclose(np.mean(list(bootstrap['base'].values())),.7)
    assert math.isclose(np.mean(list(bootstrap['adapted'].values())),.76)
    fad_variant=(1.-2.)**2+4.+1.-2.*math.sqrt(4.)
    assert fad_variant==2.
    report['numericalChecks']={'rvqMse':rvq['mse'].item(),'vaeLatent':vae['z'].item(),'diffusionInput':diff['xt'].item(),'diffusionLoss':diff['loss'].item(),'maskedVariation':altered.tolist(),'flowLongerStep':.5,'classificationCounts':evalcase['cm'].tolist(),'ablationScores':scores,'bootstrapPercentile':[float(bootstrap['low']),float(bootstrap['high'])],'firstBootstrapDraw':bootstrap['sampled'].tolist(),'fadVarianceVariation':fad_variant}
    original={theme:json.loads((ROOT/'public/courses'/f'{theme}.json').read_text(encoding='utf-8'))for theme in THEMES}
    original_ids={course['themeId']:{ch['id']:ch for ch in course['chapters']}for course in original.values()}
    fragments_by_theme={course['themeId']:course for course in courses}
    all_courses=[]
    for path in (ROOT/'public/courses').glob('*.json'):
        raw=json.loads(path.read_text(encoding='utf-8'))
        if 'chapters'in raw:all_courses.append(fragments_by_theme.get(raw['themeId'],raw))
    targets={(course['themeId'],ch['id'])for course in all_courses for ch in course['chapters']}
    scaffold_count=0;walkthrough_count=0
    for course in courses:
        assert [ch['id']for ch in course['chapters']]==list(original_ids[course['themeId']])
        for chapter in course['chapters']:
            old=original_ids[course['themeId']][chapter['id']]
            assert old['questionIds']==chapter['questionIds']and old['sourceIds']==chapter['sourceIds']
            assert not any(b.get('text','').startswith('À dire en entretien :')for b in chapter['blocks'])
            for block in chapter['blocks']:
                for linked in block.get('links',[]):assert (linked['themeId'],linked['chapterId'])in targets
                if block['type']=='walkthrough':
                    walkthrough_count+=1
                    count=len(block.get('code','').splitlines())
                    for item in block['steps']:
                        assert not item.get('lines')or all(1<=line<=count for line in item['lines']),(chapter['id'],item['title'])
                if block.get('codeMode')=='excerpt':assert block.get('requires')
            if chapter.get('checkpoint'):
                q=chapter['checkpoint'];assert len(q['options'])>=4
                options={o['id']for o in q['options']};assert q['correctOptionId']in options
                assert set(q.get('optionFeedback',{}))<=options
            if chapter.get('oral'):
                scaffold=chapter['oral']['scaffold'];assert len(scaffold['hints'])==3 and scaffold['evaluates']and scaffold['personalize']
                assert not chapter.get('checkpoint')
                assert not any('probable'in b.get('title','').lower()for b in chapter['blocks'])
                scaffold_count+=1
    report['editorialChecks']={'chapters':sum(len(c['chapters'])for c in courses),'protectedIdsQuestionsSources':True,'oralScaffolds':scaffold_count,'walkthroughLineGroupsChecked':walkthrough_count,'requiredObjectsBeforeExcerpts':True,'automaticOralEndings':0,'brokenInternalLinks':0,'browserCheck':'Not run by this content subtask; parent owns UI verification.'}
    destination=ROOT/'work/audit-generation-research-oral-evidence.json'if args.fragment else ROOT/'scripts/verify/audit-generation-research-oral-results.json'
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Saved',destination,'cases',len(report['examples']),flush=True)
if __name__=='__main__':main()
