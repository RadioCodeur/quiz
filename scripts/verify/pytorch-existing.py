"""Run every displayed Python block in the fourteen original PyTorch chapters."""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import platform
import time
from pathlib import Path
import torch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('pytorch_existing_cases',Path(__file__).with_name('pytorch-existing-cases.py'))
CASES_MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CASES_MODULE)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cases',action='store_true')
    args=parser.parse_args()
    torch.set_num_threads(1)
    course=json.loads((ROOT/'public/courses/pytorch.json').read_text('utf-8'))
    records=[]
    for chapter in course['chapters']:
        if chapter['id'] not in CASES_MODULE.CASES:continue
        blocks=([{'code':CASES_MODULE.CASES[chapter['id']],'type':'case'}] if args.cases else
                [block for block in chapter['blocks'] if block.get('code') and block.get('language','python')=='python'])
        for index,block in enumerate(blocks):
            torch.manual_seed(17)
            output=io.StringIO();start=time.perf_counter();namespace={}
            with contextlib.redirect_stdout(output):
                exec(compile(block['code'],f"{chapter['id']}:{index}",'exec'),namespace)
            records.append(dict(chapter=chapter['id'],blockIndex=index,type=block['type'],
                                sha256=hashlib.sha256(block['code'].encode()).hexdigest(),
                                seconds=round(time.perf_counter()-start,6),stdout=output.getvalue().strip()))
    evidence=dict(python=platform.python_version(),torch=torch.__version__,device='cpu',threads=1,
                  records=records,extraChecks=CASES_MODULE.extra_checks(torch))
    target=Path(__file__).with_name('pytorch-existing-results.json')
    target.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"{len(records)} blocs PyTorch exécutés ; résultats : {target.name}")

if __name__=='__main__':main()
