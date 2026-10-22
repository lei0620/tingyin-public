"""Run the shipped release APK with disposable synthetic fixtures only."""
import json
import os
import pathlib
import subprocess

inputs = json.load(open(os.environ['GITHUB_EVENT_PATH']))['inputs']
adb = ['adb', '-s', 'emulator-5580']
for path in sorted(pathlib.Path('candidate').glob('*.apk')):
    subprocess.run(adb + ['install', '-r', str(path)], check=True)
command = adb + ['shell', 'am', 'instrument', '-w', '-r',
    '-e', 'class', 'dev.neiro.app.commercial.PublicNativeTest',
    '-e', 'voucher', inputs['voucher'],
    '-e', 'davRoot', 'https://tingyin-public.0876543.xyz/qa/music/',
    '-e', 'davUser', 'qa', '-e', 'davPassword', inputs['dav_password'],
    'icu.lei2025.tingyin.publicapp.test/androidx.test.runner.AndroidJUnitRunner']
result = subprocess.run(command, capture_output=True, text=True, timeout=900)
pathlib.Path('native-evidence').mkdir(exist_ok=True)
output = result.stdout + result.stderr
for value in inputs.values():
    output = output.replace(value, '[disposable QA value]')
pathlib.Path('native-evidence/instrumentation.txt').write_text(output)
print(output)
if result.returncode or 'OK (3 tests)' not in output or 'FAILURES!!!' in output:
    raise SystemExit('Native acceptance did not pass')
