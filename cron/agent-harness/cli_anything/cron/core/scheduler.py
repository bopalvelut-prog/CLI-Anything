"""Cron job management."""
import subprocess

def list_jobs():
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
    if result.returncode != 0:
        return {"error": "No crontab found"}
    lines = [l for l in result.stdout.strip().split("\n") if l and not l.startswith("#")]
    return [{"line": i+1, "entry": e} for i, e in enumerate(lines)]

def add_job(entry):
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
    existing = result.stdout if result.returncode == 0 else ""
    new_crontab = existing.rstrip() + "\n" + entry + "\n"
    proc = subprocess.run(["crontab", "-"], input=new_crontab, capture_output=True, text=True, timeout=5)
    return {"added": entry, "returncode": proc.returncode}

def remove_job(line_num):
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
    if result.returncode != 0:
        return {"error": "No crontab found"}
    lines = result.stdout.split("\n")
    non_comment = [(i, l) for i, l in enumerate(lines) if l and not l.startswith("#")]
    if line_num > len(non_comment):
        return {"error": f"Line {line_num} not found"}
    target = non_comment[line_num - 1][1]
    new_lines = [l for l in lines if l != target]
    proc = subprocess.run(["crontab", "-"], input="\n".join(new_lines), capture_output=True, text=True, timeout=5)
    return {"removed": target, "returncode": proc.returncode}

def edit_crontab():
    return {"info": "Interactive edit not supported in CLI mode. Use add/remove commands."}

def validate_entry(entry):
    parts = entry.split(None, 5)
    if len(parts) < 6:
        return {"valid": False, "error": "Entry must have 5 time fields + command"}
    return {"valid": True, "fields": parts[:5], "command": parts[5]}
