"""File search using find."""
import subprocess

def run_search(search_path, name=None, file_type=None, size=None, mtime=None, exec_cmd=None, user=None):
    cmd = ["find", search_path]
    if name: cmd.extend(["-name", name])
    if file_type: cmd.extend(["-type", file_type])
    if size: cmd.extend(["-size", size])
    if mtime: cmd.extend(["-mtime", mtime])
    if user: cmd.extend(["-user", user])
    if exec_cmd:
        import shlex
        cmd.extend(["-exec"] + shlex.split(exec_cmd) + [";"])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        files = [f for f in result.stdout.strip().split("\n") if f][:100]
        return {"path": search_path, "count": len(files), "files": files}
    except subprocess.TimeoutExpired:
        return {"error": "Search timed out"}
