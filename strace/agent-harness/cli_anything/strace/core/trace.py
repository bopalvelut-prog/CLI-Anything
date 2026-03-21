"""Trace execution of a binary using strace."""
import subprocess,shlex

def run_trace(binary, follow=False, sys_filter=None, outfile=None, summary=False, count=False):
    cmd = ["strace"]
    if follow: cmd.append("-f")
    if summary: cmd.append("-c")
    if count: cmd.append("-C")
    if sys_filter: cmd.extend(["-e", f"trace={sys_filter}"])
    if outfile: cmd.extend(["-o", outfile])
    cmd.append(binary)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {"binary": binary, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr[:5000]}
    except subprocess.TimeoutExpired:
        return {"binary": binary, "error": "Trace timed out after 30s"}
    except FileNotFoundError:
        return {"error": "strace not found"}
