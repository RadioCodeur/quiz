"""Fetch the five specifically attributed course illustrations (no credentials)."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public' / 'media' / 'references'
FILES = {
    'speech-praat.png': 'https://upload.wikimedia.org/wikipedia/commons/3/3b/Spectrogram_-minato-.png',
    'stft-windows.svg': 'https://upload.wikimedia.org/wikipedia/commons/9/97/STFT_-_windows-en.svg',
    'mel-hertz.svg': 'https://upload.wikimedia.org/wikipedia/commons/a/aa/Mel-Hz_plot.svg',
    'cnn-convolution.png': 'https://upload.wikimedia.org/wikipedia/commons/b/bd/Convolutional_neural_network%2C_convolution_worked_example.png',
    'confusion-matrix.png': 'https://upload.wikimedia.org/wikipedia/commons/6/6f/ConfusionMatrix.png',
}


def fetch(item):
    filename, url = item
    destination = OUT / filename
    if not destination.exists():
        request = urllib.request.Request(url, headers={'User-Agent': 'RadioCodeurQuiz/1.0 (educational illustration attribution; https://github.com/RadioCodeur/quiz)'})
        with urllib.request.urlopen(request, timeout=25) as response:
            data = response.read(4_000_000)
        if not (data.startswith(b'\x89PNG') or b'<svg' in data[:1000]):
            raise ValueError(f'Unexpected image bytes: {filename}')
        destination.write_bytes(data)
    data = destination.read_bytes()
    return f'{filename}: {len(data)} bytes; SHA-256={hashlib.sha256(data).hexdigest()}'


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(fetch, FILES.items()):
            print(result)
