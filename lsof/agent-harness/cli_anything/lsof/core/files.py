"""List open files using lsof."""
import subprocess

def list_files(pid=None, port=None, user=None, file_path=None, network=False):
    cmd = ["lsof", "-F"]
    if pid: cmd.extend(["-p", str(pid)])
    if port: cmd.extend(["-i", f":{port}"])
    if user: cmd.extend(["-u", user])
    if file_path: cmd.append(file_path)
    if network: cmd.extend(["-i", "-n", "-P"])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split("\n")
        entries = []
        current = {}
        for line in lines:
            if not line: continue
            tag = line[0]; val = line[1:]
            if tag == "p": current = {"pid": val}
            elif tag == "c": current["command"] = val
            elif tag == "n": current["name"] = val; entries.append(current)
        return entries
    except FileNotFoundError:
        return {"error": "lsof not found"}
