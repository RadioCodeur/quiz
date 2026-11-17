"""Run the offline CPU examples, never imported by the website.

Use --notebooks to re-execute all twenty Jupyter documents and forty solutions.
The regular check binds unchanged notebooks to their existing execution evidence.
"""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--notebooks',action='store_true')
    args=parser.parse_args()
    commands=[['pytorch-existing.py'],['pytorch-additions.py'],['b-attention-control.py'],['b-codecs-symbolic.py'],['b-diffusion-efficiency.py'],['existing-corpus.py','--strict']]
    if args.notebooks:commands.append(['notebooks.py'])
    report={'python':platform.python_version(),'device':'cpu','commands':[],'notebooksReexecuted':args.notebooks}
    for command in commands:
        started=time.perf_counter()
        print('VERIFY '+command[0],flush=True)
        result=subprocess.run([sys.executable,str(ROOT/'scripts/verify'/command[0]),*command[1:]],cwd=ROOT)
        report['commands'].append({'script':command[0],'arguments':command[1:],'exitCode':result.returncode,'seconds':round(time.perf_counter()-started,3)})
        (ROOT/'scripts/verify/all-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        if result.returncode:return result.returncode
    return 0
if __name__=='__main__':raise SystemExit(main())
