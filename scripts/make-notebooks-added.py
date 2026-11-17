"""Build the six notebooks for the new introductory PyTorch chapters.

The displayed program is copied verbatim from the course. Exercises stay in
Markdown, so Run All remains executable before the learner fills the blanks.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDS = [
    "pytorch-en-une-page",
    "retropropagation-a-la-main",
    "boucle-entrainement-complete",
    "lire-erreurs-pytorch",
    "optimiseurs-regularisation-pratique",
    "conv-mel-autoencodeur",
]

EXERCISES = {
    "pytorch-en-une-page": [
        {
            "title": "Faire suivre un calcul par autograd",
            "prompt": "Nous multiplions un poids par trois. Complétons le calcul de sa dérivée, sans changer le poids.",
            "template": "import torch\np = torch.tensor(2., requires_grad=...)\nsortie = p * 3\ncout = sortie.square()\ncout....()\nprint(p.grad.item())",
            "solution": "import torch\np_exo = torch.tensor(2., requires_grad=True)\nsortie_exo = p_exo * 3\ncout_exo = sortie_exo.square()\ncout_exo.backward()\nassert p_exo.grad.item() == 36.0\nprint('gradient :', p_exo.grad.item())",
            "hint": "La dérivée de (3p)² est 18p. La méthode backward remplit le gradient.",
        },
        {
            "title": "Distinguer dérivée et mise à jour",
            "prompt": "Le gradient est calculé. Complétons une mise à jour de descente de gradient, avec un taux de 0,1.",
            "template": "p = torch.tensor(2., requires_grad=True)\n(p.square()).backward()\nwith torch....():\n    p -= ... * p.grad\nprint(p.item())",
            "solution": "import torch\np_exo = torch.tensor(2., requires_grad=True)\np_exo.square().backward()\navant_exo = p_exo.detach().clone()\nwith torch.no_grad():\n    p_exo -= 0.1 * p_exo.grad\nassert torch.allclose(p_exo, torch.tensor(1.6))\nassert avant_exo.item() == 2.0\nprint('poids avant et après :', avant_exo.item(), p_exo.item())",
            "hint": "backward ne change pas le poids. La soustraction constitue une opération séparée.",
        },
    ],
    "retropropagation-a-la-main": [
        {
            "title": "Écrire les dérivées locales",
            "prompt": "Retrouvons les deux gradients sans appeler PyTorch. Les valeurs sont celles du chapitre.",
            "template": "x, w1, w2 = 2., 3., -1.\nh = w1 * x\ny = w2 * h\ndL_dy = ... * y\ndL_dw2 = dL_dy * ...\ndL_dh = dL_dy * ...\ndL_dw1 = dL_dh * ...",
            "solution": "x_exo, w1_exo, w2_exo = 2.0, 3.0, -1.0\nh_exo = w1_exo * x_exo\ny_exo = w2_exo * h_exo\ndL_dy_exo = 2 * y_exo\ndL_dw2_exo = dL_dy_exo * h_exo\ndL_dh_exo = dL_dy_exo * w2_exo\ndL_dw1_exo = dL_dh_exo * x_exo\nassert (dL_dw1_exo, dL_dw2_exo) == (24.0, -72.0)\nprint('gradients manuels :', dL_dw1_exo, dL_dw2_exo)",
            "hint": "Sur chaque arête, nous multiplions le gradient reçu par la dérivée locale de l’opération.",
        },
        {
            "title": "Modifier une seule cible",
            "prompt": "Gardons x, w1 et w2. La cible devient −2. Complétons la perte et vérifions la nouvelle passe arrière.",
            "template": "w1 = torch.tensor(3., requires_grad=True)\nw2 = torch.tensor(-1., requires_grad=True)\ny = w2 * (w1 * 2)\nperte = (y - (...)).square()\nperte....()\nprint(w1.grad.item(), w2.grad.item())",
            "solution": "import torch\nw1_exo = torch.tensor(3., requires_grad=True)\nw2_exo = torch.tensor(-1., requires_grad=True)\ny_exo = w2_exo * (w1_exo * 2)\nperte_exo = (y_exo - (-2.)).square()\nperte_exo.backward()\nassert (w1_exo.grad.item(), w2_exo.grad.item()) == (16.0, -48.0)\nprint('gradients pour la cible -2 :', w1_exo.grad.item(), w2_exo.grad.item())",
            "hint": "Le nouveau gradient reçu par y vaut 2 × (y − cible). Les deux autres dérivées locales ne changent pas.",
        },
    ],
    "boucle-entrainement-complete": [
        {
            "title": "Assembler un lot et ses cibles",
            "prompt": "Complétons une fonction collate_fn. Elle reçoit une liste de couples, puis construit deux tenseurs.",
            "template": "def assembler_exemples(exemples):\n    mesures, cibles = zip(*exemples)\n    return torch....(mesures), torch....(cibles).long()",
            "solution": "import torch\ndef assembler_exemples_exo(exemples):\n    mesures, cibles = zip(*exemples)\n    return torch.stack(mesures), torch.stack(cibles).long()\nlot_exo = [(torch.tensor([1., 2., 3.]), torch.tensor(0)),\n           (torch.tensor([4., 5., 6.]), torch.tensor(1))]\nmesures_exo, cibles_exo = assembler_exemples_exo(lot_exo)\nassert mesures_exo.shape == (2, 3)\nassert cibles_exo.shape == (2,) and cibles_exo.dtype == torch.long\nprint('formes du lot :', tuple(mesures_exo.shape), tuple(cibles_exo.shape))",
            "hint": "stack ajoute l’axe des exemples. Les indices de classe restent entiers.",
        },
        {
            "title": "Moyenner une perte sur tous les exemples",
            "prompt": "Deux lots ont des tailles différentes. Complétons une moyenne qui donne le même poids à chaque exemple.",
            "template": "pertes_moyennes = [0.2, 0.8]\ntailles = [4, 1]\nsomme = sum(perte * ... for perte, n in zip(pertes_moyennes, tailles))\nmoyenne = somme / sum(...)\nprint(moyenne)",
            "solution": "pertes_moyennes_exo = [0.2, 0.8]\ntailles_exo = [4, 1]\nsomme_exo = sum(perte * n for perte, n in zip(pertes_moyennes_exo, tailles_exo))\nmoyenne_exo = somme_exo / sum(tailles_exo)\nassert abs(moyenne_exo - 0.32) < 1e-12\nprint('perte moyenne par exemple :', moyenne_exo)",
            "hint": "Nous retrouvons d’abord la somme de chaque lot, puis divisons par l’effectif total.",
        },
    ],
    "lire-erreurs-pytorch": [
        {
            "title": "Réparer le contrat de CrossEntropyLoss",
            "prompt": "Le modèle produit deux scores par exemple. Complétons le type et la forme des cibles.",
            "template": "scores = torch.tensor([[1., 2.], [3., 1.]])\ncibles = torch.tensor([1, 0], dtype=torch....)\nperte = torch.nn.CrossEntropyLoss()(scores, cibles)\nassert cibles.shape == (...)\nassert torch.isfinite(perte)",
            "solution": "import torch\nscores_exo = torch.tensor([[1., 2.], [3., 1.]])\ncibles_exo = torch.tensor([1, 0], dtype=torch.long)\nperte_exo = torch.nn.CrossEntropyLoss()(scores_exo, cibles_exo)\nassert cibles_exo.shape == (2,)\nassert torch.isfinite(perte_exo)\nprint('cibles :', cibles_exo.dtype, tuple(cibles_exo.shape))",
            "hint": "Pour les cibles entières de cet exemple, la perte attend un indice long par ligne.",
        },
        {
            "title": "Aplatir une transposée sans supposer sa contiguïté",
            "prompt": "Nous voulons les valeurs dans l’ordre logique du tenseur transposé. Complétons une opération adaptée.",
            "template": "x = torch.arange(6).reshape(2, 3).t()\nplat = x....(6)\nassert plat.tolist() == [...]",
            "solution": "import torch\nx_exo = torch.arange(6).reshape(2, 3).t()\nplat_exo = x_exo.reshape(6)\nassert plat_exo.tolist() == [0, 3, 1, 4, 2, 5]\nprint('ordre après transposition :', plat_exo.tolist())",
            "hint": "reshape peut copier si nécessaire. Il ne transforme pas une transposition en l’ordre d’origine.",
        },
    ],
    "optimiseurs-regularisation-pratique": [
        {
            "title": "Contrôler une mise à jour SGD",
            "prompt": "Nous minimisons w² à partir de w=1. Complétons une étape SGD sans régularisation, avec lr=0,1.",
            "template": "w = torch.nn.Parameter(torch.tensor(1.))\nopt = torch.optim.SGD([w], lr=...)\nopt....(set_to_none=True)\nw.square().backward()\nopt....()\nprint(w.item())",
            "solution": "import torch\nw_exo = torch.nn.Parameter(torch.tensor(1.))\nopt_exo = torch.optim.SGD([w_exo], lr=0.1)\nopt_exo.zero_grad(set_to_none=True)\nw_exo.square().backward()\nopt_exo.step()\nassert torch.allclose(w_exo, torch.tensor(0.8))\nprint('poids après SGD :', w_exo.item())",
            "hint": "Le gradient vaut deux. La règle soustrait lr × gradient.",
        },
        {
            "title": "Séparer scheduler et arrêt anticipé",
            "prompt": "Une validation s’améliore puis stagne. Complétons le compteur d’attente pour une patience de deux observations.",
            "template": "meilleure = float('inf')\nattente = 0\nfor epoch, val in enumerate([0.5, 0.4, 0.41, 0.42], start=1):\n    if val < meilleure:\n        meilleure, attente = val, ...\n    else:\n        attente += ...\n    if attente >= ...:\n        print('arret', epoch)\n        break",
            "solution": "meilleure_exo, attente_exo = float('inf'), 0\narret_exo = None\nfor epoch_exo, val_exo in enumerate([0.5, 0.4, 0.41, 0.42], start=1):\n    if val_exo < meilleure_exo:\n        meilleure_exo, attente_exo = val_exo, 0\n    else:\n        attente_exo += 1\n    if attente_exo >= 2:\n        arret_exo = epoch_exo\n        break\nassert arret_exo == 4 and meilleure_exo == 0.4\nprint('arrêt à l’époque :', arret_exo)",
            "hint": "Ce compteur décide quand arrêter. Un scheduler déciderait comment modifier le taux d’apprentissage.",
        },
    ],
    "conv-mel-autoencodeur": [
        {
            "title": "Prévoir la forme d’une convolution",
            "prompt": "Nous réduisons les deux dimensions d’une carte mel. Complétons les paramètres puis vérifions la forme.",
            "template": "entree = torch.zeros(2, 1, 64, 96)\nconv = torch.nn.Conv2d(1, 4, kernel_size=3, stride=..., padding=...)\nsortie = conv(entree)\nassert tuple(sortie.shape) == (...)",
            "solution": "import torch\nentree_exo = torch.zeros(2, 1, 64, 96)\nconv_exo = torch.nn.Conv2d(1, 4, kernel_size=3, stride=2, padding=1)\nsortie_exo = conv_exo(entree_exo)\nassert tuple(sortie_exo.shape) == (2, 4, 32, 48)\nprint('forme après convolution :', tuple(sortie_exo.shape))",
            "hint": "Le nombre d’exemples reste deux. Les quatre filtres deviennent quatre canaux de sortie.",
        },
        {
            "title": "Lire une perte de reconstruction",
            "prompt": "Une seule case présente une erreur de un, parmi quatre cases. Complétons le calcul de MSE.",
            "template": "cible = torch.tensor([0., 0., 0., 1.])\nreconstruction = torch.zeros(4)\nperte = ((reconstruction - cible) ** ...).mean()\nassert perte.item() == ...",
            "solution": "import torch\ncible_exo = torch.tensor([0., 0., 0., 1.])\nreconstruction_exo = torch.zeros(4)\nperte_exo = ((reconstruction_exo - cible_exo) ** 2).mean()\nassert perte_exo.item() == 0.25\nprint('MSE :', perte_exo.item())",
            "hint": "La moyenne porte sur quatre erreurs au carré. Une faible MSE ne garantit pas seule une bonne écoute.",
        },
    ],
}


def markdown(identifier: str, source: str) -> dict:
    return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": source}


def code(identifier: str, source: str, tags: list[str] | None = None) -> dict:
    return {
        "cell_type": "code", "id": identifier,
        "metadata": {"tags": tags or []}, "source": source,
        "execution_count": None, "outputs": [],
    }


def make_notebook(chapter: dict) -> dict:
    identifier = chapter["id"]
    programs = [
        block["code"] for block in chapter["blocks"]
        if block.get("code") and block.get("language", "python") == "python"
    ]
    assert len(programs) == 1, (identifier, len(programs))
    program = programs[0]
    exercises = EXERCISES[identifier]
    notes = [
        "Nous exécutons ce notebook avec un noyau Python neuf, sur CPU.",
        "Version vérifiée : Python 3.11.9, PyTorch 2.10.0 et TorchAudio 2.10.0.",
        "Les cellules n’installent aucun paquet et ne téléchargent aucune donnée.",
        "Les nombres du cours viennent de cette version ; une autre version peut modifier certains arrondis ou messages.",
        "Dans Colab, choisissons un environnement sans accélérateur, puis Exécution → Tout exécuter.",
        "Les trous des exercices restent dans du Markdown : ils ne cassent donc pas l’exécution complète.",
    ]
    if identifier == "conv-mel-autoencodeur":
        notes.append("Les deux ondes de ce programme sont synthétiques. Elles ne sont pas les enregistrements réels du laboratoire audio.")
    if identifier == "lire-erreurs-pytorch":
        notes.append("Les erreurs sont provoquées puis interceptées. Le cas de placement oppose meta et CPU ; il ne mesure pas un appareil CUDA.")
    if identifier == "optimiseurs-regularisation-pratique":
        notes.append("La branche CUDA est montrée pour la lecture. L’exécution vérifiée est CPU ; aucune accélération GPU n’est revendiquée.")

    setup = """import os
import sys
import tempfile

# À lancer dans un noyau neuf : ce tutoriel reste sur CPU.
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import torch
torch.set_num_threads(1)
torch.manual_seed(17)
print("Python :", sys.version.split()[0])
print("PyTorch :", torch.__version__)
print("CUDA visible :", torch.cuda.is_available())
_quiz_initial_directory = os.getcwd()
_quiz_temporary_directory = tempfile.TemporaryDirectory(prefix="quiz-pytorch-")
os.chdir(_quiz_temporary_directory.name)
"""
    if identifier == "conv-mel-autoencodeur":
        setup += "import torchaudio\nprint(\"TorchAudio :\", torchaudio.__version__)\n"
    setup += "assert not torch.cuda.is_available(), 'Choisir un noyau CPU neuf pour ce notebook.'"

    walkthrough = next(block for block in chapter["blocks"] if block["type"] == "walkthrough")
    step_text = "## Nous lisons le programme\n\n" + "\n\n".join(
        f"**{index + 1}. {step['title']}**\n\n{step['text']}"
        for index, step in enumerate(walkthrough["steps"])
    )
    cells = [
        markdown("objectif", f"# {chapter['title']}\n\n{chapter['summary']}\n\n" + "\n\n".join(notes)),
        markdown("cours", f"[Relire le chapitre](https://radiocodeur.github.io/quiz/cours.html?theme=pytorch#{identifier}).\n\nLe programme suivant est copié à l’identique depuis le cours."),
        code("environnement", setup, ["environment"]),
        markdown("lecture", step_text),
        code("programme-du-cours", program, ["course-program"]),
        markdown("interpretation", "## Interpréter avant de modifier\n\n" + walkthrough["result"] + "\n\n" + "\n\n".join(chapter["takeaways"])),
    ]
    for index, exercise in enumerate(exercises, start=1):
        text = (
            f"## Exercice {index} — {exercise['title']}\n\n{exercise['prompt']}\n\n"
            "Copions ce squelette dans une nouvelle cellule, puis remplaçons les `...`.\n\n"
            f"```python\n{exercise['template']}\n```\n\n"
            f"**Piste :** {exercise['hint']}"
        )
        cell = markdown(f"exercice-{index}", text)
        cell["metadata"]["tags"] = ["exercise"]
        cells.append(cell)

    cells.append(code("nettoyage", "os.chdir(_quiz_initial_directory)\n_quiz_temporary_directory.cleanup()\nprint('Programme terminé ; fichiers temporaires supprimés.')", ["cleanup"]))
    solutions = "## Solutions — ouvrons-les après notre recherche\n\n"
    solutions += "Les solutions utilisent leurs propres variables. Nous pouvons les copier dans de nouvelles cellules.\n\n"
    for index, exercise in enumerate(exercises, start=1):
        solutions += (
            f"<details>\n<summary>Afficher la solution {index} — {html.escape(exercise['title'])}</summary>\n\n"
            f"<pre><code>{html.escape(exercise['solution'])}</code></pre>\n\n</details>\n\n"
        )
    cell = markdown("solutions", solutions)
    cell["metadata"]["tags"] = ["solutions"]
    cells.append(cell)
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11.9"},
            "colab": {"name": f"{identifier}.ipynb", "provenance": []},
            "quiz": {
                "chapterId": identifier,
                "themeId": "pytorch",
                "sourceCodeSha256": hashlib.sha256(program.encode("utf-8")).hexdigest(),
                "device": "cpu",
                "verifiedVersions": {"python": "3.11.9", "torch": "2.10.0", "torchaudio": "2.10.0"},
                "exerciseSolutions": [exercise["solution"] for exercise in exercises],
            },
        },
        "cells": cells,
    }


def main() -> None:
    course = json.loads((ROOT / "public/courses/pytorch.json").read_text("utf-8"))
    chapters = {chapter["id"]: chapter for chapter in course["chapters"]}
    destination = ROOT / "public/notebooks"
    destination.mkdir(parents=True, exist_ok=True)
    for identifier in IDS:
        notebook = make_notebook(chapters[identifier])
        (destination / f"{identifier}.ipynb").write_text(
            json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print("Six notebooks des nouveaux chapitres créés.")


if __name__ == "__main__":
    main()
