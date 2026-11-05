#!/usr/bin/env bash
# Process substitution gives Bash a transient /dev/fd source. Download a real
# local copy before running so /usr/local/bin/selfsteal retains this edition.
if [[ "${BASH_SOURCE[0]:-}" == /dev/fd/* || "${BASH_SOURCE[0]:-}" == /proc/self/fd/* ]]; then
    # Drain the original pipe so curl can finish normally while the real copy runs.
    cat -- "${BASH_SOURCE[0]}" >/dev/null || true
    selfsteal_bootstrap=$(mktemp "${TMPDIR:-/tmp}/selfsteal.XXXXXXXX.sh") || exit 1
    trap 'rm -f -- "$selfsteal_bootstrap"' EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    if ! command -v curl >/dev/null 2>&1; then
        printf 'Для загрузки установите curl.\n' >&2
        exit 1
    fi
    if ! curl -fLsS --retry 2 --connect-timeout 15 --max-time 180 '__INSTALLER_URL__' -o "$selfsteal_bootstrap" || ! bash -n "$selfsteal_bootstrap"; then
        printf 'Не удалось получить полную копию Selfsteal из GitHub.\n' >&2
        exit 1
    fi
    bash "$selfsteal_bootstrap" "$@"
    selfsteal_bootstrap_status=$?
    exit "$selfsteal_bootstrap_status"
fi
