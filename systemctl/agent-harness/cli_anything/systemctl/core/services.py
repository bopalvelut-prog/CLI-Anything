"""Systemd service management."""
import subprocess

def _run(args):
    result = subprocess.run(["systemctl"] + args, capture_output=True, text=True, timeout=15)
    return {"returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}

def service_status(service):
    return _run(["status", service])

def start_service(service):
    return _run(["start", service])

def stop_service(service):
    return _run(["stop", service])

def restart_service(service):
    return _run(["restart", service])

def enable_service(service):
    return _run(["enable", service])

def disable_service(service):
    return _run(["disable", service])

def list_units(unit_type=None):
    args = ["list-units", "--no-pager", "--plain"]
    if unit_type: args.extend(["--type", unit_type])
    result = subprocess.run(["systemctl"] + args, capture_output=True, text=True, timeout=15)
    lines = result.stdout.strip().split("\n")[:50]
    units = []
    for line in lines:
        parts = line.split(None, 4)
        if len(parts) >= 4:
            units.append({"unit": parts[0], "load": parts[1], "active": parts[2], "sub": parts[3], "description": parts[4] if len(parts) > 4 else ""})
    return units

def show_journal(service, lines=50):
    result = subprocess.run(["journalctl", "-u", service, "-n", str(lines), "--no-pager"], capture_output=True, text=True, timeout=15)
    return result.stdout.strip().split("\n")

def mask_service(service):
    return _run(["mask", service])

def reload_service(service):
    return _run(["reload", service])
