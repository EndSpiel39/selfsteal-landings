"""Validate payload, offline exports and directory-preserving replacement."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
from build_site import ROOT, page

BASH = 'C:/Program Files/Git/bin/bash.exe' if os.name == 'nt' else 'bash'
script = (ROOT/'selfsteal.sh').read_text(encoding='utf-8')
subprocess.run([BASH, '-n', str(ROOT/'selfsteal.sh')], check=True)
payload = re.search("base64 -d <<'RYADOM_BUNDLE_BASE64'\n(.*?)\nRYADOM_BUNDLE_BASE64", script, re.S).group(1)
bundle = base64.b64decode(payload)
info = json.loads((ROOT/'build-info.json').read_text())
assert hashlib.sha256(bundle).hexdigest() == info['bundle_sha256']
assert hashlib.sha256((ROOT/'selfsteal.sh').read_bytes()).hexdigest() == info['script_sha256']
with tarfile.open(fileobj=io.BytesIO(bundle),mode='r:gz') as archive:
    for member in archive.getmembers():
        assert not member.name.startswith('/') and '..' not in Path(member.name).parts
        assert member.isfile()
    for number in range(1,12):
        html = archive.extractfile(f'templates/{number}.html').read().decode()
        assert html == page(number-1, 'assets/')
        assert '<form' not in html and '__ASSETS__' not in html
        if number>1:
            assert 'YouTube' in html and 'Telegram' in html
        assert 'Twitter' not in html
        assert '<title>' in archive.extractfile(f'templates/{number}.404.html').read().decode()
    titles = [re.search(r'<title>(.*?)</title>',archive.extractfile(f'templates/{n}.html').read().decode()).group(1) for n in range(1,12)]
    assert len(set(titles)) == 11, 'Every site must have its own product identity'
    for asset in (ROOT/'site/assets').rglob('*'):
        if asset.is_file():
            assert archive.extractfile(f'assets/{asset.relative_to(ROOT/"site/assets").as_posix()}').read() == asset.read_bytes()

def shell_path(path):
    return str(path).replace('\\','/')

# All mutations, including mktemp cleanup by the Linux-target script, stay inside
# this verified workspace-owned scratch root. The production installer is not run.
scratch_parent = ROOT/'tools'/'qa'/'scratch'
scratch_parent.mkdir(exist_ok=True)
assert scratch_parent.resolve().is_relative_to(ROOT.resolve())
with tempfile.TemporaryDirectory(dir=scratch_parent) as scratch:
    task_env = {**os.environ,'TMPDIR':shell_path(Path(scratch))}
    for number in range(1,12):
        target = Path(scratch)/f'export-{number}'
        assert target.resolve().is_relative_to(scratch_parent.resolve())
        result = subprocess.run([BASH,str(ROOT/'selfsteal.sh'),'export-template',str(number),shell_path(target)],env=task_env,text=True,encoding='utf-8',capture_output=True)
        assert result.returncode == 0, result.stdout+result.stderr
        assert (target/'index.html').read_text(encoding='utf-8') == page(number-1,'assets/')
        assert (target/'assets/manrope.ttf').exists()
    custom = script[script.index('# Bundled Ryadom templates.'):script.index('# Function to show template options')]
    app = Path(scratch)/'app'
    app.mkdir()
    html = app/'html'
    html.mkdir()
    (html/'previous.txt').write_text('previous-site')
    harness = f'''set -euo pipefail
log_error() {{ printf '%s\\n' "$*" >&2; }}
log_info() {{ :; }}
log_success() {{ :; }}
create_dir_safe() {{ mkdir -p -- "$1"; }}
declare -A TEMPLATE_NAMES=([1]=one [2]=two)
APP_DIR='{shell_path(app)}'
HTML_DIR="$APP_DIR/html"
{custom}
download_template 2
test -s "$HTML_DIR/index.html"
test ! -e "$HTML_DIR/previous.txt"
test "$(cat "$APP_DIR"/.ryadom-backup.*/previous.txt)" = previous-site
before=$(sha256sum "$HTML_DIR/index.html")
if download_template 99; then exit 21; fi
test "$before" = "$(sha256sum "$HTML_DIR/index.html")"
if export_template_command 1 "$HTML_DIR"; then exit 22; fi
test "$before" = "$(sha256sum "$HTML_DIR/index.html")"
# A failed staged copy must restore all previous website files.
cp() {{
  if [[ "${{1:-}}" = '-a' && "${{3:-}}" = *'.ryadom-stage.'* ]]; then touch "$APP_DIR/simulated-copy-failure"; return 1; fi
  command cp "$@"
}}
if download_template 1; then exit 23; fi
test -f "$APP_DIR/simulated-copy-failure"
test "$before" = "$(sha256sum "$HTML_DIR/index.html")"
'''
    result = subprocess.run([BASH],input=harness,env=task_env,text=True,encoding='utf-8',capture_output=True)
    assert result.returncode==0, result.stdout+result.stderr
    assert html.exists()
print('PASS: Bash syntax, payload integrity, 11 offline exports, full asset set, invalid-ID rejection, backup, existing-directory protection, copy-failure rollback.')
