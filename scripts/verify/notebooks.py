"""Execute each delivered notebook and its hidden exercise solutions on CPU.

Run with the isolated notebook runtime documented in VERIFICATION.md.
No network request, dataset download or package installation is performed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2]

def one(path):
    import nbformat
    from nbclient import NotebookClient
    notebook=nbformat.read(path,as_version=4)
    nbformat.validate(notebook)
    course=json.loads((ROOT/'public/courses/pytorch.json').read_text(encoding='utf-8'))
    chapter=next(chapter for chapter in course['chapters'] if chapter['id']==notebook.metadata.quiz.chapterId)
    cell_by_id={cell.id:cell for cell in notebook.cells}
    programs=notebook.metadata.quiz.get('programs',[])
    displayed=[(index,block)for index,block in enumerate(chapter['blocks'])if block.get('code')and block.get('language','python')=='python']
    assert len(programs)==len(displayed),'Chaque programme du cours possède ses cellules progressives'
    for program,(index,block)in zip(programs,displayed):
        assert program['blockIndex']==index
        reconstructed=''.join(cell_by_id[id].source for id in program['cellIds'])
        assert reconstructed==block['code'],'Les cellules doivent conserver exactement le programme du cours'
        assert hashlib.sha256(reconstructed.encode()).hexdigest()==program['sourceSha256']
    exercise_cells=[cell for cell in notebook.cells if 'exercise'in cell.metadata.get('tags',[])]
    assert len(exercise_cells)==2 and all(cell.cell_type=='code'for cell in exercise_cells),'Deux vrais espaces de pratique exécutables'
    source_hash=hashlib.sha256(json.dumps([cell.source for cell in notebook.cells],ensure_ascii=False).encode()).hexdigest()
    original_count=len(notebook.cells)
    solutions=notebook.metadata.get('quiz',{}).get('exerciseSolutions',[])
    assert len(solutions)==2,'Deux solutions exécutables par notebook'
    for index,solution in enumerate(solutions):
        notebook.cells.append(nbformat.v4.new_code_cell(solution,metadata={'tags':['verification-only'],'jupyter':{'source_hidden':True}}))
    started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='quiz-notebook-') as folder:
        client=NotebookClient(notebook,timeout=100,kernel_name='python3',allow_errors=False,resources={'metadata':{'path':folder}})
        client.km=client.create_kernel_manager()
        # Use this exact Python environment, without registering a user kernel.
        client.km.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
        executed=client.execute()
    elapsed=time.perf_counter()-started
    assert elapsed<120,f'Notebook trop long : {elapsed:.2f}s'
    solution_outputs=[]
    for cell in executed.cells[original_count:]:
        solution_outputs.append([output.get('text','') for output in cell.get('outputs',[]) if output.output_type=='stream'])
    executed.cells=executed.cells[:original_count]
    exercise_outputs=[]
    for cell in executed.cells:
        if 'exercise'in cell.metadata.get('tags',[]):
            output=''.join(item.get('text','')for item in cell.outputs if item.output_type=='stream')
            assert 'À compléter'in output and 'Contrôle réussi'not in output,'Un exercice vide ne doit pas annoncer une réussite'
            exercise_outputs.append(output)
    executed.metadata.quiz.update(verifiedDevice='cpu',verifiedSeconds=round(elapsed,3),verifiedPython=platform.python_version())
    nbformat.validate(executed)
    nbformat.write(executed,path)
    notebook_hash=hashlib.sha256(json.dumps(json.loads(path.read_text('utf-8')),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    record={'path':str(path.relative_to(ROOT)).replace('\\','/'),'sourceSha256':source_hash,'notebookSha256':notebook_hash,'elapsedSeconds':round(elapsed,3),'device':'cpu','codeCells':sum(cell.cell_type=='code' for cell in executed.cells),'exerciseSolutions':2,'solutionOutputs':solution_outputs,'exerciseDefaultOutputs':exercise_outputs,'programsVerified':len(programs),'exerciseCellsReady':2,'unfinishedExercisesReported':2}
    return record

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--one');args=parser.parse_args()
    if args.one:
        print(json.dumps(one(Path(args.one).resolve()),ensure_ascii=False));return
    os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1';os.environ['NUMBA_DISABLE_JIT']='1'
    course=json.loads((ROOT/'public/courses/pytorch.json').read_text(encoding='utf-8'))
    paths=[chapter.get('notebook')for chapter in course['chapters']]
    assert all(path==f'notebooks/{chapter["id"]}.ipynb'for path,chapter in zip(paths,course['chapters'])),'Tous les chapitres doivent posséder un notebook lié'
    assert len(set(paths))==len(paths),'Un fichier distinct par chapitre'
    notebooks=[ROOT/'public'/path for path in paths]
    assert all(path.is_file()for path in notebooks),'Tous les notebooks liés sont présents'
    records=[]
    for path in notebooks:
        print('Exécution CPU : '+path.stem,flush=True)
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--one',str(path)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120,env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        if result.returncode:
            print(result.stdout);print(result.stderr,file=sys.stderr);raise RuntimeError(path.name)
        record=json.loads(result.stdout.strip().splitlines()[-1]);records.append(record)
        print(f"  terminé en {record['elapsedSeconds']} s",flush=True)
    from importlib.metadata import version
    report={'python':platform.python_version(),'torch':version('torch'),'torchaudio':version('torchaudio'),'nbformat':version('nbformat'),'nbclient':version('nbclient'),'device':'cpu','limitSeconds':120,'linkedChapters':len(paths),'notebooks':records}
    (ROOT/'scripts/verify/notebooks-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(records)} notebooks exécutés, solutions comprises.',flush=True)

if __name__=='__main__':main()
