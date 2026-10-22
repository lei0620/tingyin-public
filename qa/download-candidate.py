"""Download an authenticated, temporary QA artifact; no repository write token."""
import base64
import hashlib
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor

inputs = json.load(open(os.environ['GITHUB_EVENT_PATH']))['inputs']
authorization = 'Basic ' + base64.b64encode(('qa:' + inputs['dav_password']).encode()).decode()
root = Path('candidate')
root.mkdir(exist_ok=True)

def fetch(name):
    request = Request('https://tingyin-public.0876543.xyz/qa/candidate/' + name,
                      headers={'Authorization': authorization, 'User-Agent': 'Tingyin-Public-Native-QA/1.0 (+https://github.com/lei0620/tingyin-public)'})
    try:
        with urlopen(request, timeout=120) as response:
            data = response.read()
    except HTTPError as error:
        detail=error.read(800).decode(errors='replace').replace(authorization,'[QA authorization]').replace(inputs['dav_password'],'[QA password]')
        print('Candidate HTTP diagnostic:',error.code,error.headers.get('Server'),detail)
        raise
    (root / name).write_bytes(data)
    return data

manifest = json.loads(fetch('candidate-manifest.json'))
with ThreadPoolExecutor(max_workers=4) as executor:
    parts = list(executor.map(fetch, [f'app-release.apk.part{i:03d}' for i in range(manifest['parts'])]))
data = b''.join(parts)
assert len(data) == manifest['bytes'] and hashlib.sha256(data).hexdigest() == manifest['sha256']
(root / 'app-release.apk').write_bytes(data)
fetch('app-release-androidTest.apk')
print('Exact signed candidate APK SHA-256 verified')
