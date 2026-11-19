"""Execute the revised data/advanced PyTorch examples, outside the website."""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import runpy
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2]
OWNED={'dataset-et-batches','padding-et-collate','moyennes-masquees','detacher-geler-journaliser','moyennes-et-microbatches','sauvegarder-et-reprendre','optimiseurs-regularisation-pratique','scheduler-et-arret-anticipe','cuda-amp-memoire','preparer-mel-pour-conv','convolution-a-la-main','conv-mel-autoencodeur','lire-erreurs-pytorch','boucle-entrainement-complete'}

def numeric_checks(ns,torch):
    checks=[]
    def check(condition,label):
        assert condition,label
        checks.append(label)
    if 'premier_de_nouveau'in ns:
        check(tuple(ns['mesures'].shape)==(3,2),'three fixed rows, two descriptors')
        check(ns['annotations'].tolist()==[0,1],'first batch keeps labels')
        check(ns['dernieres_cibles'].tolist()==[0],'last batch keeps final label')
        check(ns['premier_de_nouveau'][1].tolist()==[0,1],'a new iterator starts again')
    if 'lot_du_loader'in ns:
        check(tuple(ns['batch'].shape)==(2,2,2),'padding batch axes')
        check(ns['masque'].tolist()==[[True,True],[True,False]],'validity from lengths')
        check(torch.equal(ns['lot_du_loader'][0],ns['batch']),'DataLoader invokes same collate function')
    if 'denominateur'in ns:
        check(tuple(ns['validite'].shape)==(2,2,1),'mask expands descriptors')
        check(torch.allclose(ns['moyennes'],torch.tensor([[.15,2.],[.2,4.5]])),'masked means')
        check(ns['denominateur'].item()==6,'six elementary valid values')
        check(abs(ns['numerateur'].item()-28.84)<1e-4,'sum of squared descriptor values')
    if 'nombre'in ns:
        check(ns['nombre']==1. and isinstance(ns['nombre'],float),'item returns a Python float')
        check(ns['valeurs'].tolist()==[1.,2.]and ns['copie'].tolist()==[99.,2.],'clone protects original storage')
        check(not ns['detachees'].requires_grad and ns['copie_avec_graphe'].requires_grad,'detach and clone have different graph effects')
        check(ns['poids'].grad.item()==-2.,'logging did not destroy the learning graph')
    if 'tete'in ns:
        check(all(p.grad is None for p in ns['encodeur'].parameters()),'frozen encoder has no parameter gradients')
        check(all(p.grad is not None for p in ns['tete'].parameters()),'trainable head has gradients')
    if 'moyenne_globale'in ns:
        check(ns['moyenne_globale']==2.6 and ns['moyenne_des_lots']==3.5,'weighted and unweighted means differ')
    if 'gradient_complet'in ns:
        check(ns['gradient_complet']==ns['gradient_decoupe']==-15.,'weighted microbatch gradients match')
        check(torch.allclose(ns['poids_complet'],ns['poids_decoupe']),'single updates match')
    if 'scores_avant'in ns:
        check(ns['scores_avant'].tolist()==[[4.5,-4.5]],'known inference scores')
        check(torch.equal(ns['scores_avant'],ns['scores_apres']),'save/load preserves inference')
    if 'nouvel_optimiseur'in ns:
        check(len(ns['nouvel_optimiseur'].state)==2,'two parameter tensors have Adam state')
        check(torch.equal(ns['modele'].weight,ns['copie'].weight),'model state reloaded')
    if 'type_optimiseur'in ns:
        check(ns['gradient']==-2.,'same scalar loss gradient')
        check(abs(ns['poids'].item()-1.09)<1e-6,'first AdamW step with decay')
    if 'validations_fictives'in ns:
        check(ns['epoque']==4 and ns['attente']==2,'patience stops on fourth chosen validation')
        check(ns['meilleure']==.6,'best chosen validation retained')
        check(abs(ns['poids'].item()-1.36)<1e-6,'best weight restored')
    if 'norme_avant'in ns:
        check(ns['norme_avant'].item()==10.,'clipping returns original norm')
        check(abs(ns['poids'].grad.item()-1)<1e-5,'gradient clipped before step')
    if 'amp_active'in ns:
        check(ns['device'].type=='cpu' and not ns['amp_active'],'CPU path, no CUDA measurement')
        check(ns['octets_poids']==24,'six float32 parameters')
    if 'mel_court'in ns:
        check(tuple(ns['stft'].shape)==(2,201,98) and ns['stft'].is_complex(),'STFT complex axes')
        check(tuple(ns['mel'].shape)==(2,64,98),'mel axes')
        check(tuple(ns['entree'].shape)==(2,1,64,96),'cropped four-axis model input')
        check(torch.isfinite(ns['entree']).all().item(),'finite logarithmic input')
    if 'noyau'in ns:
        check(ns['produits'].tolist()==[[1.,0.],[0.,-5.]],'visible first kernel products')
        check(ns['sortie'][0,0].tolist()==[[-4.,-4.],[-4.,-4.]],'kernel reused at four positions')
        check(ns['variante'][0,0].tolist()==[[-3.,-2.],[0.,1.]],'one weight changes each local sum')
        check(tuple(torch.nn.Conv1d(1,8,5,stride=1,padding=0)(torch.zeros(4,1,100)).shape)==(4,8,96),'Conv1d extension preserves examples and produces eight learned channels')
    if 'decodeur'in ns:
        check(abs(ns['avant']-.8759986758232117)<1e-6,'reference reconstruction loss')
        check(ns['apres']<ns['avant'],'this measured step reduces this reconstruction loss')
    if 'transpose'in ns:
        check(ns['transpose'].reshape(6).tolist()==[0,3,1,4,2,5],'reshape follows transposed order')
        check(ns['poids'].grad.item()==4.,'gradient appears after backward')
    if 'historique'in ns:
        check(len(ns['historique'])==5,'five complete epochs')
        check(len(ns['train'])==128 and len(ns['validation'])==64,'separate synthetic datasets')
        check(ns['identique'],'full program inference survives loading')
    if 'bruit_choisi'in ns:
        check(ns['centres'].tolist()==[[-1.],[1.],[-1.]],'class indices map to cloud centers')
        check(torch.allclose(ns['mesures'],torch.tensor([[-1.,-.8,-1.2],[1.2,1.,.8],[-1.2,-1.,-.8]])),'chosen perturbations yield announced coordinates')
    return checks

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--draft',action='store_true')
    parser.add_argument('--fragment')
    parser.add_argument('--output',default='scripts/verify/audit-pytorch-advanced-results.json')
    args=parser.parse_args()
    os.environ['CUDA_VISIBLE_DEVICES']=''
    import torch
    torch.set_num_threads(1)
    if args.draft:
        codes=runpy.run_path(str(ROOT/'work/make-pytorch-advanced.py'))['CODES']
        cases=[(name,source)for name,source in codes.items()]
    else:
        path=ROOT/(args.fragment or 'public/courses/pytorch.json')
        data=json.loads(path.read_text(encoding='utf-8'))
        cases=[(chapter['id']+'/'+str(index),block['code'])for chapter in data['chapters']if chapter['id']in OWNED for index,block in enumerate(chapter['blocks'])if block.get('code')and block.get('language','python')=='python']
    report={'python':platform.python_version(),'torch':torch.__version__,'device':'cpu','threads':1,'examples':[],'limits':['CUDA branch is present but not executed on this CPU build.','All acoustic features and signals in these programs are pedagogical choices or synthetic signals, not measurements of the listening-lab files.']}
    for name,source in cases:
        started=time.perf_counter();buffer=io.StringIO();namespace={}
        with tempfile.TemporaryDirectory(prefix='quiz-audit-')as folder:
            previous=Path.cwd()
            try:
                os.chdir(folder)
                torch.manual_seed(17)
                with contextlib.redirect_stdout(buffer):exec(compile(source,name,'exec'),namespace)
            finally:os.chdir(previous)
        values={}
        for key,value in namespace.items():
            if isinstance(value,torch.Tensor):
                values[key]={'shape':list(value.shape),'dtype':str(value.dtype),'requiresGrad':value.requires_grad,'values':value.detach().cpu().tolist() if value.numel()<=24 else None}
            elif isinstance(value,(float,int,bool,str)):values[key]=value
            elif key=='historique':values[key]=value
        assertions=numeric_checks(namespace,torch)
        report['examples'].append({'name':name,'codeSha256':hashlib.sha256(source.encode()).hexdigest(),'stdout':buffer.getvalue(),'seconds':round(time.perf_counter()-started,6),'values':values,'assertions':assertions})
        print(name,'CPU OK',flush=True)
    destination=ROOT/args.output
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Executed:',len(cases))

if __name__=='__main__':main()
