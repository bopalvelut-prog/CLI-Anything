"""Text editing using sed."""
import subprocess

def sed_replace(filepath, pattern, replacement, inplace=False):
    cmd = ["sed"]
    if inplace: cmd.append("-i")
    cmd.extend([f"s/{pattern}/{replacement}/g", filepath])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return {"file": filepath, "pattern": pattern, "replacement": replacement, "output": result.stdout[:5000]}

def sed_delete(filepath, line_num):
    cmd = ["sed", f"{line_num}d", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return {"file": filepath, "deleted_line": line_num, "output": result.stdout[:5000]}

def sed_insert(filepath, line_num, text):
    cmd = ["sed", f"{line_num}i\\{text}", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return {"file": filepath, "inserted_at": line_num, "text": text, "output": result.stdout[:5000]}

def sed_extract(filepath, pattern):
    cmd = ["sed", f"-n", f"/{pattern}/p", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return {"file": filepath, "pattern": pattern, "matches": result.stdout.strip().split("\n")}
