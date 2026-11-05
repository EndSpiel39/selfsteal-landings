"""Exercise terminal choices, replacement routing and FD bootstrap safely."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
from build_site import ROOT

BASH = 'C:/Program Files/Git/bin/bash.exe' if os.name == 'nt' else 'bash'
source = (ROOT/'selfsteal.sh').read_text(encoding='utf-8')
runtime = (ROOT/'tools/installer_runtime.sh').read_text(encoding='utf-8')
registry = re.search(r'declare -A TEMPLATE_NAMES=\(.*?\n\)',source,re.S).group()
scratch_parent = ROOT/'tools/qa/scratch'
scratch_parent.mkdir(exist_ok=True)
assert scratch_parent.resolve().is_relative_to(ROOT.resolve())
with tempfile.TemporaryDirectory(dir=scratch_parent) as temp:
    scratch = Path(temp)
    assert scratch.resolve().is_relative_to(scratch_parent.resolve())
    task_env = {**os.environ,'TMPDIR':str(scratch).replace('\\','/')}
    harness = f'''set -euo pipefail
log_error() {{ printf '%s\\n' "$*" >&2; }}
check_running_as_root() {{ :; }}
APP_DIR='{str(scratch).replace(chr(92),'/')}'
HTML_DIR="$APP_DIR/html"
mkdir "$HTML_DIR"
touch "$APP_DIR/docker-compose.yml"
{registry}
{runtime}
FORCE_MODE=false
FORCE_TEMPLATE=''
select_install_template <<<'5'
test "$SELECTED_TEMPLATE" = 5
select_install_template <<< $'bad\\n\\n11'
test "$SELECTED_TEMPLATE" = 11
select_install_template <<<'r'
test "$SELECTED_TEMPLATE" -ge 1 && test "$SELECTED_TEMPLATE" -le 11
if select_install_template <<<'0'; then exit 11; fi
if select_install_template </dev/null; then exit 12; fi
FORCE_MODE=true
if select_install_template; then exit 13; fi
FORCE_TEMPLATE=2
select_install_template
test "$SELECTED_TEMPLATE" = 2
FORCE_TEMPLATE=random
for attempt in $(seq 1 30); do
 select_install_template
 test "$SELECTED_TEMPLATE" -ge 1 && test "$SELECTED_TEMPLATE" -le 11
done
download_template() {{ printf '%s' "$1" > "$APP_DIR/chosen"; }}
install_management_script() {{ touch "$APP_DIR/manager-updated"; }}
show_current_template_info() {{ printf 'current-template\\n'; }}
FORCE_MODE=false
FORCE_TEMPLATE=''
template_command <<<'8'
test "$(cat "$APP_DIR/chosen")" = 8
test -f "$APP_DIR/manager-updated"
FORCE_TEMPLATE=random
template_command
test "$(cat "$APP_DIR/chosen")" -ge 1
test "$(cat "$APP_DIR/chosen")" -le 11
'''
    result = subprocess.run([BASH],input=harness,text=True,encoding='utf-8',capture_output=True,env=task_env)
    assert result.returncode==0,result.stdout+result.stderr
    # Simulate curl in the process-substitution path; never contact GitHub here.
    script_path=str(ROOT/'selfsteal.sh').replace('\\','/')
    bootstrap_test = f'''set -euo pipefail
curl() {{ local last="${{@: -1}}"; cp -- '{script_path}' "$last"; }}
export -f curl
bash <(cat '{script_path}') @ --version
'''
    result = subprocess.run([BASH],input=bootstrap_test,text=True,encoding='utf-8',capture_output=True,env=task_env)
    assert result.returncode==0,result.stdout+result.stderr
    assert '2.11.1-landings.2' in result.stdout,result.stdout
print('PASS: numbered/invalid/random/cancel/EOF choices, explicit selection, noninteractive requirements, existing-install routing, management adoption, and bash <(curl ...) @ argument preservation.')
