"""Screen session management."""
import subprocess

def list_sessions():
    result = subprocess.run(["screen", "-ls"], capture_output=True, text=True, timeout=5)
    lines = result.stdout.strip().split("\n")
    sessions = []
    for line in lines:
        line = line.strip()
        if "." in line and "(" in line:
            parts = line.split("\t")
            sessions.append({"session": parts[0], "status": parts[1] if len(parts) > 1 else ""})
    return sessions

def create_session(name):
    result = subprocess.run(["screen", "-dmS", name], capture_output=True, text=True, timeout=5)
    return {"created": name, "returncode": result.returncode}

def attach_session(name):
    return {"info": f"Attach to '{name}' with: screen -r {name}"}

def detach_session(name):
    result = subprocess.run(["screen", "-d", name], capture_output=True, text=True, timeout=5)
    return {"detached": name, "returncode": result.returncode}

def kill_session(name):
    result = subprocess.run(["screen", "-S", name, "-X", "quit"], capture_output=True, text=True, timeout=5)
    return {"killed": name, "returncode": result.returncode}

def send_command(name, command):
    result = subprocess.run(["screen", "-S", name, "-X", "stuff", f"{command}\n"], capture_output=True, text=True, timeout=5)
    return {"sent": command, "to": name, "returncode": result.returncode}
