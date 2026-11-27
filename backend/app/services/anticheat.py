import logging
import shlex

from paramiko import SSHClient

from .ssh import execute_command, upload_script

logger = logging.getLogger(__name__)

SCRIPT_NAME = "schoollinux_anticheat"
SCRIPT_PATH = f"/tmp/{SCRIPT_NAME}.sh"
PID_FILE = f"/tmp/{SCRIPT_NAME}.pid"
LOG_FILE = f"/tmp/{SCRIPT_NAME}.log"
SYSTEMD_UNIT = "schoollinux-anticheat"

# GUI file managers that can be used to browse the student's files during a game.
# Matching is done against both /proc/<pid>/comm and the basename of /proc/<pid>/exe.
FILE_MANAGERS = (
    "nautilus",
    "nemo",
    "thunar",
    "dolphin",
    "pcmanfm",
    "pcmanfm-qt",
    "caja",
    "krusader",
    "konqueror",
    "spacefm",
    "rox-filer",
    "rox",
    "doublecmd",
    "doublecmd-gtk",
    "dde-file-manager",
    "peony",
    "pantheon-files",
    "gnome-commander",
)

_TARGETS_BLOCK = "\n".join(f"  {name}" for name in FILE_MANAGERS)

ANTICHEAT_START_COMMAND = f"""
unit="{SYSTEMD_UNIT}"
script="{SCRIPT_PATH}"
pid_file="{PID_FILE}"
log_file="{LOG_FILE}"
started=0

# A plain background process is killed when the SSH session scope ends.
# Run as a transient user service so it survives the SSH connection.
if command -v systemd-run >/dev/null 2>&1 && systemctl --user show-environment >/dev/null 2>&1; then
    if systemd-run --user --unit="$unit" --collect \
        --property=Type=simple \
        --property=Restart=on-failure \
        --property=RestartSec=1 \
        /bin/bash "$script" >/dev/null; then
        started=1
    fi
fi

# Fallback for systems without a user systemd manager.
if [ "$started" -eq 0 ] && command -v at >/dev/null 2>&1 && systemctl is-active --quiet atd >/dev/null 2>&1; then
    if echo "/bin/bash $script >$log_file 2>&1" | at now >/dev/null 2>&1; then
        started=1
    fi
fi

# Last-resort fallback. It may not survive the SSH session on all systems.
if [ "$started" -eq 0 ]; then
    if command -v setsid >/dev/null 2>&1; then
        setsid nohup /bin/bash "$script" >"$log_file" 2>&1 < /dev/null &
    else
        nohup /bin/bash "$script" >"$log_file" 2>&1 < /dev/null &
    fi
fi

for _ in 1 2 3 4 5 6 7 8 9 10; do
    [ -s "$pid_file" ] && break
    sleep 0.1
done
cat "$pid_file" 2>/dev/null || true
"""

ANTICHEAT_SCRIPT = f"""#!/bin/bash
set -u

PID_FILE="{PID_FILE}"
SCRIPT_PATH="{SCRIPT_PATH}"

TARGETS=(
{_TARGETS_BLOCK}
)

cleanup() {{
    rm -f "$PID_FILE"
}}
trap cleanup EXIT
trap 'exit 0' TERM INT

# Stop a previously running instance before registering this one.
if [ -f "$PID_FILE" ]; then
    old_pid="$(head -n 1 "$PID_FILE" 2>/dev/null || true)"
    if [ -n "$old_pid" ] && [ "$old_pid" != "$$" ] && [ -r "/proc/$old_pid/cmdline" ]; then
        old_cmd="$(tr '\\0' ' ' < "/proc/$old_pid/cmdline" 2>/dev/null || true)"
        case "$old_cmd" in
            *"$SCRIPT_PATH"*)
                kill -9 "$old_pid" 2>/dev/null || true
                ;;
        esac
    fi
fi

echo "$$" > "$PID_FILE"

is_target() {{
    local name="$1"
    local target
    [ -z "$name" ] && return 1
    for target in "${{TARGETS[@]}}"; do
        if [ "$name" = "$target" ]; then
            return 0
        fi
        # /proc/<pid>/comm is limited to 15 characters.
        if [ "${{#target}}" -gt 15 ] && [ "$name" = "${{target:0:15}}" ]; then
            return 0
        fi
    done
    return 1
}}

collect_descendants() {{
    local pid="$1"
    local child
    for child in $(cat "/proc/$pid/task/$pid/children" 2>/dev/null || true); do
        collect_descendants "$child"
    done
    echo "$pid"
}}

while true; do
    for proc_dir in /proc/[0-9]*; do
        pid="${{proc_dir##*/}}"
        [ "$pid" = "$$" ] && continue
        [ -r "$proc_dir/comm" ] || continue

        comm="$(cat "$proc_dir/comm" 2>/dev/null || true)"
        exe_path="$(readlink "$proc_dir/exe" 2>/dev/null || true)"
        exe_name="${{exe_path##*/}}"

        if is_target "$comm" || is_target "$exe_name"; then
            for victim in $(collect_descendants "$pid"); do
                kill -9 "$victim" 2>/dev/null || true
            done
        fi
    done
    sleep 1
done
"""


def start_anticheat(client: SSHClient) -> int | None:
    """Upload and start the anticheat loop in the background."""
    # Remove leftovers from a previous game before replacing the script file.
    stop_anticheat(client)

    upload_script(client, SCRIPT_NAME, ANTICHEAT_SCRIPT)
    stdout, stderr = execute_command(
        client, f"bash -c {shlex.quote(ANTICHEAT_START_COMMAND)}"
    )

    raw_pid = stdout.strip().splitlines()
    pid = None
    if raw_pid and raw_pid[-1].strip().isdigit():
        pid = int(raw_pid[-1].strip())

    if pid is None:
        logger.warning(
            "Anticheat started without a readable PID. stdout=%r stderr=%r",
            stdout,
            stderr,
        )
    else:
        logger.info("Anticheat started with PID %s", pid)

    return pid


def stop_anticheat(client: SSHClient) -> None:
    """Stop the anticheat process and remove its remote files."""
    command = f"""
unit="{SYSTEMD_UNIT}"
pid_file="{PID_FILE}"
script_path="{SCRIPT_PATH}"

if command -v systemctl >/dev/null 2>&1; then
    systemctl --user stop "$unit.service" >/dev/null 2>&1 || true
    systemctl --user reset-failed "$unit.service" >/dev/null 2>&1 || true
fi

pid=""
if [ -f "$pid_file" ]; then
    pid="$(head -n 1 "$pid_file" 2>/dev/null || true)"
fi
case "$pid" in
    ''|*[!0-9]*) pid="" ;;
esac
if [ -n "$pid" ] && [ -r "/proc/$pid/cmdline" ]; then
    cmd="$(tr '\\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)"
    case "$cmd" in
        *"$script_path"*)
            kill -9 "$pid" 2>/dev/null || true
            ;;
    esac
fi
rm -f "$pid_file" "$script_path"
exit 0
"""
    execute_command(client, f"bash -c {shlex.quote(command)}")
    logger.info("Anticheat stopped")
