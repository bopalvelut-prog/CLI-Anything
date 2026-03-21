"""Text processing using awk."""
import subprocess

def awk_filter(filepath, program=None, field=None, pattern=None, action=None):
    if program:
        cmd = ["awk", program, filepath]
    elif field:
        cmd = ["awk", f"{{print ${field}}}", filepath]
    elif pattern and action:
        cmd = ["awk", f"/{pattern}/ {{ {action} }}", filepath]
    else:
        cmd = ["awk", "{print}", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    lines = result.stdout.strip().split("\n")[:100]
    return {"file": filepath, "lines": lines, "count": len(lines)}

def awk_sum(filepath, column):
    cmd = ["awk", f"{{sum += ${column}}} END {{print sum}}", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return {"file": filepath, "column": column, "sum": result.stdout.strip()}

def awk_count(filepath, pattern):
    cmd = ["awk", f"/{pattern}/ {{count++}} END {{print count}}", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return {"file": filepath, "pattern": pattern, "count": result.stdout.strip()}
