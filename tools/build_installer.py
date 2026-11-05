"""Package a standalone Selfsteal fork with all eleven bundled templates."""
from pathlib import Path
import base64
import gzip
import hashlib
import io
import json
import re
import tarfile
from build_site import ROOT, SITE, VARIANTS, page, build

CUSTOM_FUNCTIONS = r'''
# Bundled Ryadom templates. No remote template fetches or brand mutation.
ryadom_bundle() {
    base64 -d <<'RYADOM_BUNDLE_BASE64'
__BUNDLE__
RYADOM_BUNDLE_BASE64
}

write_ryadom_template() {
    local template_id="$1" destination="$2" stage
    if ! [[ "$template_id" =~ ^([1-9]|10|11)$ ]]; then
        log_error "Template must be a number from 1 to 11"
        return 1
    fi
    stage=$(mktemp -d) || return 1
    if ! ryadom_bundle | tar -xzf - -C "$stage"; then
        rm -rf -- "$stage"
        log_error "Could not extract the bundled landing"
        return 1
    fi
    if [ ! -s "$stage/templates/$template_id.html" ] || [ ! -s "$stage/assets/app.js" ] || [ ! -s "$stage/assets/mountains.jpg" ]; then
        rm -rf -- "$stage"
        log_error "Bundled template is incomplete"
        return 1
    fi
    if ! mkdir -p -- "$destination" || ! cp -R -- "$stage/assets" "$destination/" || ! cp -- "$stage/templates/$template_id.html" "$destination/index.html" || ! cp -- "$stage/templates/$template_id.404.html" "$destination/404.html"; then
        rm -rf -- "$stage"
        return 1
    fi
    rm -rf -- "$stage"
}

setup_file_permissions() {
    find "$HTML_DIR" -type d -exec chmod 755 {} +
    find "$HTML_DIR" -type f -exec chmod 644 {} +
}

download_template() {
    local template_id="$1" stage backup
    if [[ -z "${TEMPLATE_NAMES[$template_id]:-}" ]]; then
        log_error "Unknown template: $template_id"
        return 1
    fi
    # Keep the HTML directory itself: Docker may bind-mount this inode.
    if [ -z "${APP_DIR:-}" ] || [ "$APP_DIR" = / ] || [ "$HTML_DIR" != "$APP_DIR/html" ] || [ -L "$HTML_DIR" ]; then
        log_error "Refusing an unexpected website directory: $HTML_DIR"
        return 1
    fi
    create_dir_safe "$APP_DIR" || return 1
    create_dir_safe "$HTML_DIR" || return 1
    stage=$(mktemp -d "$APP_DIR/.ryadom-stage.XXXXXX") || return 1
    if ! write_ryadom_template "$template_id" "$stage"; then
        rm -rf -- "$stage"
        return 1
    fi
    backup=$(mktemp -d "$APP_DIR/.ryadom-backup.XXXXXX") || { rm -rf -- "$stage"; return 1; }
    if ! cp -a -- "$HTML_DIR/." "$backup/"; then
        rm -rf -- "$stage" "$backup"
        return 1
    fi
    if ! find "$HTML_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + || ! cp -a -- "$stage/." "$HTML_DIR/" || ! setup_file_permissions; then
        log_error "Template installation failed; restoring the previous website"
        find "$HTML_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} + || true
        cp -a -- "$backup/." "$HTML_DIR/" || log_error "Restore failed. Backup remains at $backup"
        rm -rf -- "$stage"
        return 1
    fi
    rm -rf -- "$stage"
    log_success "Installed: ${TEMPLATE_NAMES[$template_id]}"
    log_info "Previous website backup: $backup"
}

create_default_html() {
    download_template 1
}

export_template_command() {
    local template_id="${1:-1}" destination="${2:-./ryadom-export}"
    if [ -e "$destination" ] || [ -L "$destination" ]; then
        log_error "Export destination already exists; choose a new directory: $destination"
        return 1
    fi
    write_ryadom_template "$template_id" "$destination" || return 1
    printf 'Exported template %s to %s\n' "$template_id" "$destination"
}

'''

def replace_function(source, name, replacement):
    pattern = rf'(?m)^{re.escape(name)}\(\) \{{\n.*?^\}}'
    source, count = re.subn(pattern, lambda m: replacement, source, count=1, flags=re.S)
    assert count == 1, name
    return source

def package():
    build()
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w') as archive:
        def add(name, data):
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(data), 0o644, 0
            archive.addfile(info, io.BytesIO(data))
        for i in range(11):
            add(f'templates/{i+1}.html', page(i, 'assets/').encode())
            name = 'Рядом' if i == 0 else VARIANTS[i][0]
            error_page = (SITE/'404.html').read_text(encoding='utf-8').replace('Рядом', name)
            add(f'templates/{i+1}.404.html', error_page.encode())
        for asset in sorted((SITE/'assets').rglob('*')):
            if asset.is_file():
                add(f'assets/{asset.relative_to(SITE/"assets").as_posix()}', asset.read_bytes())
        add('404.html', (SITE/'404.html').read_bytes())
    bundle = gzip.compress(raw.getvalue(), compresslevel=9, mtime=0)
    encoded = base64.b64encode(bundle).decode()
    bundle_b64 = '\n'.join(encoded[offset:offset+100] for offset in range(0,len(encoded),100))
    script = (ROOT/'selfsteal.upstream.sh').read_text(encoding='utf-8')
    script = script.replace('SCRIPT_VERSION="2.11.1"', 'SCRIPT_VERSION="2.11.1-landings.2"')
    installer_url = 'https://raw.githubusercontent.com/EndSpiel39/selfsteal-landings/main/selfsteal.sh'
    script = script.replace('SCRIPT_URL="https://raw.githubusercontent.com/dignezzz/remnawave-scripts/main/selfsteal.sh"', f'SCRIPT_URL="{installer_url}"')
    bootstrap = (ROOT/'tools/bootstrap.sh').read_text(encoding='utf-8').replace('__INSTALLER_URL__', installer_url)
    script = bootstrap + '\n' + script.split('\n', 1)[1]
    # No remote update may replace this custom installer with upstream.
    for name in ['check_for_updates', 'update_script']:
        script = replace_function(script, name, f'''{name}() {{
    echo "Ryadom custom edition: automatic upstream updates are disabled."
    echo "Rebuild this custom selfsteal.sh to retain the bundled landings."
}}''')
    script = replace_function(script, 'check_for_updates_silent', 'check_for_updates_silent() {\n    return 0\n}')
    folders = 'declare -A TEMPLATE_FOLDERS=(\n' + '\n'.join(f'    ["{i+1}"]="ryadom-{i+1}"' for i in range(11)) + '\n)'
    names = 'declare -A TEMPLATE_NAMES=(\n' + '\n'.join(f'    ["{i+1}"]="{ "Рядом — Кинозал" if i==0 else v[0]}"' for i,v in enumerate(VARIANTS)) + '\n)'
    script = re.sub(r'declare -A TEMPLATE_FOLDERS=\(.*?\n\)', lambda _: folders, script, count=1, flags=re.S)
    script = re.sub(r'declare -A TEMPLATE_NAMES=\(.*?\n\)', lambda _: names, script, count=1, flags=re.S)
    start = script.index('# ============================================\n# Template Mutation')
    end = script.index('# Function to show template options', start)
    script = script[:start] + CUSTOM_FUNCTIONS.replace('__BUNDLE__', bundle_b64) + script[end:]
    start = script.index('    # List of available templates', script.index('install_command()'))
    end = script.index('    # Install management script', start)
    script = script[:start] + '''    local selected_template="$SELECTED_TEMPLATE"
    local selected_name="${TEMPLATE_NAMES[$selected_template]:-}"
    local installed_template=""
    if [ -z "$selected_name" ]; then
        log_error "Template must be a number from 1 to 11"
        return 1
    fi
    if download_template "$selected_template"; then
        installed_template="$selected_name"
    else
        log_error "Could not install the selected Ryadom landing; no generic fallback was substituted"
        return 1
    fi

''' + script[end:]
    marker = '    # Check if already installed (any server)'
    assert marker in script
    script = script.replace(marker, '    select_install_template || return $?\n\n' + marker, 1)
    # An on-disk file copies itself; process substitution must not fetch upstream.
    start = script.index('    else\n        local temp_script="/tmp/selfsteal-install.sh"', script.index('install_management_script()'))
    end = script.index('    \n    if [ -f "$script_path" ]; then', start)
    script = script[:start] + '''    else
        log_error "Save this custom selfsteal.sh to a local file before installing."
        log_error "Run: sudo bash ./selfsteal.sh install"
        return 1
    fi
''' + script[end:]
    # /dev/fd is not a persistent source for the management script.
    script = script.replace('if [ -f "$0" ] && [ "$0" != "bash" ] && [ "$0" != "@" ]; then', 'if [ -f "$0" ] && [[ "$0" != /dev/fd/* ]] && [ "$0" != "bash" ] && [ "$0" != "@" ]; then')
    # Guard before setup, and add an offline, unprivileged export command.
    dispatch = '# Auto-detect existing installation if server wasn\'t specified via command line'
    runtime = (ROOT/'tools/installer_runtime.sh').read_text(encoding='utf-8')
    script = script.replace(dispatch, runtime + '\n' + '''# Reject invalid choices before the installer changes server configuration.
if [ -n "$FORCE_TEMPLATE" ] && ! [[ "$FORCE_TEMPLATE" =~ ^([1-9]|10|11|random|r|R)$ ]]; then
    log_error "Укажите --template 1..11 или --template random"
    exit 1
fi
if [ "$COMMAND" = "export-template" ]; then
    export_template_command "${ARGS[@]}"
    exit $?
fi
''' + dispatch)
    script = script.replace('if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then\n                FORCE_TEMPLATE="$2"', 'if [ -n "${2:-}" ] && [[ "$2" =~ ^([1-9]|10|11|random|r|R)$ ]]; then\n                FORCE_TEMPLATE="$2"')
    script = script.replace('if ! [[ "$FORCE_TEMPLATE" =~ ^[0-9]+$ ]]; then', 'if ! [[ "$FORCE_TEMPLATE" =~ ^([1-9]|10|11|random|r|R)$ ]]; then')
    script = script.replace('--template requires a template number (1-11)', '--template requires 1..11 or random')
    script = script.replace('"Don\'t mutate templates on install"', '"Compatibility flag; Ryadom keeps its curated branding"')
    script = script.replace('"Template number to install"', '"Landing 1..11 or random; asks when omitted"').replace('--template <1-11>', '--template <1-11|random>')
    script = script.replace('show_help() {', 'show_help() {\n    echo "Ryadom edition: 11 bundled co-watching landings; offline export: selfsteal export-template ID NEW_DIRECTORY"')
    script = script.replace('        --help|-h)\n            show_help\n            exit 0\n', '        --help|-h)\n            COMMAND="help"\n            shift\n')
    # User-requested template switching is CLI-friendly and never restarts services unnecessarily.
    # template_command is replaced by the runtime above, including direct IDs,
    # random selection, backups, and adoption of the new management script.
    license_text = (ROOT/'LICENSE.upstream').read_text(encoding='utf-8')
    script += '\n# Upstream license notice, retained in the standalone distribution.\n' + '\n'.join('# ' + line for line in license_text.splitlines()) + '\n'
    (ROOT/'selfsteal.sh').write_text(script, encoding='utf-8', newline='\n')
    provenance = {
        'upstream':'https://raw.githubusercontent.com/DigneZzZ/remnawave-scripts/main/selfsteal.sh',
        'downloaded':'2026-11-05',
        'upstream_sha256':hashlib.sha256((ROOT/'selfsteal.upstream.sh').read_bytes()).hexdigest(),
        'bundle_sha256':hashlib.sha256(bundle).hexdigest(),
        'script_sha256':hashlib.sha256((ROOT/'selfsteal.sh').read_bytes()).hexdigest(),
        'template_count':11,
    }
    (ROOT/'build-info.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Standalone installer built: {len(script.encode()):,} bytes; bundle {len(bundle):,} bytes.')

if __name__ == '__main__':
    package()
