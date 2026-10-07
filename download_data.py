"""Download the input data for all figure and table scripts from Zenodo into data/."""

import hashlib
import sys
import zipfile
from pathlib import Path

import requests

ZENODO_RECORD = '23210248'  # dataset record, doi:10.5281/zenodo.23210248
DATA_DIR = Path(__file__).resolve().parent / 'data'


def main():
    api = f'https://zenodo.org/api/records/{ZENODO_RECORD}'
    response = requests.get(api, timeout=60)
    response.raise_for_status()
    files = response.json()['files']
    DATA_DIR.mkdir(exist_ok=True)
    for entry in files:
        name = entry['key']
        target = DATA_DIR / name
        if target.exists() and target.stat().st_size == entry['size']:
            print(f'{name}: already present')
            continue
        print(f'{name}: downloading ({entry["size"] / 1e6:.1f} MB)')
        with requests.get(entry['links']['self'], stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(target, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
        algo, expected = entry['checksum'].split(':', 1)
        digest = hashlib.new(algo)
        with open(target, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                digest.update(chunk)
        if digest.hexdigest() != expected:
            target.unlink()
            sys.exit(f'{name}: checksum mismatch, please run download_data.py again')
        if target.suffix == '.zip':
            with zipfile.ZipFile(target) as z:
                z.extractall(DATA_DIR)
            target.unlink()
    print(f'Data ready in {DATA_DIR}')


if __name__ == '__main__':
    sys.exit(main())
