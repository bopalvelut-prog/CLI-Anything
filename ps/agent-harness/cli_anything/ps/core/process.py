"""Process management using ps."""
import subprocess

def list_processes(user=None):
    cmd = ["ps", "aux"]
    if user: cmd.extend(["-u", user])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    lines = result.stdout.strip().split("\n")
    procs = []
    for line in lines[1:]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            procs.append({"user": parts[0], "pid": parts[1], "cpu": parts[2], "mem": parts[3], "command": parts[10][:80]})
    return procs

def process_tree():
    result = subprocess.run(["ps", "axjf"], capture_output=True, text=True, timeout=10)
    return result.stdout.strip().split("\n")[:50]

def process_info(pid):
    result = subprocess.run(["ps", "-p", str(pid), "-o", "pid,ppid,user,%cpu,%mem,vsz,rss,stat,start,time,command"], capture_output=True, text=True, timeout=10)
    return result.stdout.strip()

def kill_process(pid=None, name=None):
    if pid:
        subprocess.run(["kill", str(pid)], capture_output=True, text=True, timeout=5)
        return {"killed": f"PID {pid}"}
    elif name:
        result = subprocess.run(["pkill", name], capture_output=True, text=True, timeout=5)
        return {"killed": name, "returncode": result.returncode}
    return {"error": "Provide --pid or --name"}

def top_processes():
    result = subprocess.run(["ps", "aux", "--sort=-%cpu"], capture_output=True, text=True, timeout=10)
    lines = result.stdout.strip().split("\n")[:15]
    procs = []
    for line in lines[1:]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            procs.append({"user": parts[0], "pid": parts[1], "cpu": parts[2], "mem": parts[3], "command": parts[10][:60]})
    return procs
