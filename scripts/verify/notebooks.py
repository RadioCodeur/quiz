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
    assert not notebook.metadata.quiz.get('notebookAlias'),'Un renvoi Markdown ne doit pas être exécuté'
    course=json.loads((ROOT/'public/courses/pytorch.json').read_text(encoding='utf-8'))
    chapter=next(chapter for chapter in course['chapters'] if chapter['id']==notebook.metadata.quiz.chapterId)
    cell_by_id={cell.id:cell for cell in notebook.cells}
    programs=notebook.metadata.quiz.get('programs',[])
    displayed=[(index,block)for index,block in enumerate(chapter['blocks'])if block.get('readingCompanion')and block.get('code')and block.get('language','python')=='python']
    assert len(programs)==len(displayed),'Chaque programme du cours possède ses cellules progressives'
    checks=json.loads((ROOT/'scripts/verify/narration-pytorch-checks.json').read_text('utf-8'))
    for program,(index,block)in zip(programs,displayed):
        assert program['blockIndex']==index
        assert program['programId']==block['programId']
        reconstructed=''.join(cell_by_id[id].source for id in program['cellIds'])
        assert reconstructed==block['code'],'Les cellules doivent conserver exactement le programme du cours'
        assert hashlib.sha256(reconstructed.encode()).hexdigest()==program['sourceSha256']
        assert all(cell_by_id[id].metadata.programId==program['programId'] for id in program['cellIds'])
        expressions=checks[chapter['id']+'/'+program['programId']]
        assert program['assertions']==expressions and len(expressions)>=2
        expected='\n'.join('assert bool('+expression+'), '+repr(chapter['id']+'/'+program['programId']+': '+expression)for expression in expressions)
        expected+='\nprint("Contrôles numériques de la démonstration réussis.")'
        assert cell_by_id[program['assertionCellId']].source==expected
    exercise_cells=[cell for cell in notebook.cells if 'exercise'in cell.metadata.get('tags',[])]
    assert len(exercise_cells)==2 and all(cell.cell_type=='code'for cell in exercise_cells),'Deux vrais espaces de pratique exécutables'
    source_hash=hashlib.sha256(json.dumps([cell.source for cell in notebook.cells],ensure_ascii=False).encode()).hexdigest()
    solutions=notebook.metadata.get('quiz',{}).get('exerciseSolutions',[])
    assert len(solutions)==2,'Deux solutions exécutables par notebook'
    cleanup_index=next(index for index,cell in enumerate(notebook.cells)if 'cleanup'in cell.metadata.get('tags',[]))
    solution_cells=[]
    for index,solution in enumerate(solutions):
        solution_cells.append(nbformat.v4.new_code_cell(solution,id='verify-solution-'+str(index+1),metadata={'tags':['verification-only'],'jupyter':{'source_hidden':True}}))
    # Solutions may save a checkpoint; run them before the temporary folder is
    # cleaned up, so verification cannot leave files in the repository.
    solution_ids={cell.id for cell in solution_cells}
    notebook.cells[cleanup_index:cleanup_index]=solution_cells
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
    for cell in executed.cells:
        if cell.id in solution_ids:
            outputs=[output.get('text','')for output in cell.get('outputs',[])if output.output_type=='stream']
            assert 'Contrôle réussi' in ''.join(outputs),'La solution doit passer ses assertions'
            solution_outputs.append(outputs)
    executed.cells=[cell for cell in executed.cells if cell.id not in solution_ids]
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
    record={'path':str(path.relative_to(ROOT)).replace('\\','/'),'sourceSha256':source_hash,'notebookSha256':notebook_hash,'elapsedSeconds':round(elapsed,3),'device':'cpu','codeCells':sum(cell.cell_type=='code' for cell in executed.cells),'exerciseSolutions':2,'solutionOutputs':solution_outputs,'exerciseDefaultOutputs':exercise_outputs,'programsVerified':len(programs),'programIds':[program['programId']for program in programs],'numericalAssertions':sum(len(program['assertions'])for program in programs),'exerciseCellsReady':2,'unfinishedExercisesReported':2}
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
    aliases=[]
    for previous,target in course.get('notebookAliases',{}).items():
        assert target in paths and previous not in paths,'Le renvoi cible directement un notebook canonique'
        alias_path=ROOT/'public'/previous
        alias=json.loads(alias_path.read_text('utf-8'))
        assert alias['metadata']['quiz']['notebookAlias']==target
        assert alias['cells']and all(cell['cell_type']=='markdown'for cell in alias['cells']),'Un ancien fichier ne conserve pas de code périmé'
        assert target in '\n'.join(cell['source']if isinstance(cell['source'],str)else''.join(cell['source'])for cell in alias['cells'])
        canonical=json.dumps(json.loads(alias_path.read_text('utf-8')),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        aliases.append({'path':'public/'+previous,'target':'public/'+target,'codeCells':0,'hashFormat':'canonical-json','sha256':hashlib.sha256(canonical).hexdigest()})
    records=[]
    for path in notebooks:
        print('Exécution CPU : '+path.stem,flush=True)
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--one',str(path)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120,env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        if result.returncode:
            print(result.stdout);print(result.stderr,file=sys.stderr);raise RuntimeError(path.name)
        record=json.loads(result.stdout.strip().splitlines()[-1]);records.append(record)
        print(f"  terminé en {record['elapsedSeconds']} s",flush=True)
    from importlib.metadata import version
    report={'python':platform.python_version(),'torch':version('torch'),'torchaudio':version('torchaudio'),'nbformat':version('nbformat'),'nbclient':version('nbclient'),'device':'cpu','limitSeconds':120,'linkedChapters':len(paths),'notebooks':records,'aliases':aliases}
    (ROOT/'scripts/verify/notebooks-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(records)} notebooks exécutés, solutions comprises ; {len(aliases)} renvois Markdown vérifiés sans exécution.',flush=True)

if __name__=='__main__':main()
