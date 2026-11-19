"""Execute the authoritative PyTorch companion programs and bind reading slices.

The short fragments are checked against exact lines of their complete program;
they are not claimed to run independently of the preceding instructions.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2]

def run(course,checks):
    os.environ['CUDA_VISIBLE_DEVICES']=''
    import torch
    torch.set_num_threads(1)
    report={'python':platform.python_version(),'torch':torch.__version__,'device':'cpu','threads':1,'programs':[],'fragments':[],'limits':['The CUDA branches are not executed on this CPU runtime.','The classification descriptors and reserved examples are chosen; the mel signals are synthetic.','Reading fragments are exact slices of executed complete programs, not standalone executions.']}
    for chapter in course['chapters']:
        programs={block['programId']:block for block in chapter['blocks'] if block.get('readingCompanion')}
        assert programs,chapter['id']+': programme autonome manquant'
        for program_id,block in programs.items():
            key=chapter['id']+'/'+program_id
            assert len(checks.get(key,[]))>=2,key+': contrôles numériques manquants'
            namespace={'__name__':'__main__'}
            buffer=io.StringIO()
            started=time.perf_counter()
            with tempfile.TemporaryDirectory(prefix='quiz-narration-')as folder:
                previous=Path.cwd()
                try:
                    os.chdir(folder)
                    torch.manual_seed(17)
                    with contextlib.redirect_stdout(buffer):exec(compile(block['code'],key,'exec'),namespace)
                    for expression in checks[key]:
                        assert bool(eval(expression,namespace)),key+': '+expression
                finally:os.chdir(previous)
            values={}
            for name,value in namespace.items():
                if isinstance(value,torch.Tensor):
                    values[name]={'shape':list(value.shape),'dtype':str(value.dtype),'requiresGrad':value.requires_grad,'values':value.detach().cpu().tolist()if value.numel()<=32 else None}
                elif isinstance(value,(float,int,bool,str)):values[name]=value
                elif isinstance(value,list)and len(value)<=8 and all(isinstance(item,(float,int,bool,str))for item in value):values[name]=value
            report['programs'].append({'chapterId':chapter['id'],'programId':program_id,'sha256':hashlib.sha256(block['code'].encode()).hexdigest(),'stdout':buffer.getvalue(),'seconds':round(time.perf_counter()-started,6),'assertions':checks[key],'values':values})
            print(key+' CPU OK',flush=True)
        for block in chapter['blocks']:
            if block.get('role')!='reading-fragment':continue
            program=programs[block['programId']]
            first,last=block['sourceLines']
            source='\n'.join(program['code'].split('\n')[first-1:last])
            assert source.removesuffix('\n')==block['code'].removesuffix('\n'),chapter['id']+': extrait différent du programme exécuté'
            report['fragments'].append({'chapterId':chapter['id'],'programId':block['programId'],'sourceLines':[first,last],'sha256':hashlib.sha256(block['code'].encode()).hexdigest(),'programSha256':hashlib.sha256(program['code'].encode()).hexdigest()})
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--fragment',default='public/courses/pytorch.json')
    parser.add_argument('--checks',default='scripts/verify/narration-pytorch-checks.json')
    parser.add_argument('--output',default='scripts/verify/narration-pytorch-results.json')
    args=parser.parse_args()
    course=json.loads((ROOT/args.fragment).read_text('utf-8'))
    checks=json.loads((ROOT/args.checks).read_text('utf-8'))
    report=run(course,checks)
    (ROOT/args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"{len(report['programs'])} programmes exécutés, {len(report['fragments'])} extraits liés aux programmes.",flush=True)

if __name__=='__main__':main()
