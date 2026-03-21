"""FreeCAD CLI - Script generation and execution engine.

Generates FreeCAD Python scripts and executes them via freecadcmd headless mode.
"""

import json
import os
import subprocess
import tempfile
from typing import Dict, Any, Optional, List


def find_freecadcmd() -> str:
    """Find freecadcmd binary on the system."""
    candidates = [
        "freecadcmd",
        "/usr/bin/freecadcmd",
        "/usr/local/bin/freecadcmd",
        "/Applications/FreeCAD.app/Contents/MacOS/freecadcmd",
        "C:\\Program Files\\FreeCAD\\bin\\freecadcmd.exe",
    ]
    for cmd in candidates:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    raise RuntimeError(
        "freecadcmd not found. Install FreeCAD: apt install freecad freecad-python3"
    )


def run_script(script: str, timeout: int = 300) -> Dict[str, Any]:
    """Execute a FreeCAD Python script via freecadcmd.

    Returns dict with status, stdout, stderr, and parsed JSON output if present.
    """
    freecadcmd = find_freecadcmd()

    # Write script to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(
            [freecadcmd, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "FREECAD_USER_HOME": os.path.expanduser("~")},
        )

        # Try to parse JSON from the last line of stdout
        output = None
        stdout_lines = result.stdout.strip().split("\n")
        for line in reversed(stdout_lines):
            line = line.strip()
            if line.startswith("{") or line.startswith("["):
                try:
                    output = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue

        return {
            "status": "success" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output": output,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Script timed out after {timeout}s",
            "stderr": "",
        }
    finally:
        os.unlink(script_path)


def wrap_script(body: str, output_var: str = "result") -> str:
    """Wrap body code in a FreeCAD script with JSON output."""
    return f"""#!/usr/bin/env python3
import sys
import json
import os

try:
    import FreeCAD
    import Part
except ImportError:
    print(json.dumps({{"error": "FreeCAD Python module not found", "type": "import_error"}}))
    sys.exit(1)

{body}

try:
    print(json.dumps({output_var}, default=str))
except NameError:
    print(json.dumps({{"status": "success"}}))
except Exception as e:
    print(json.dumps({{"error": str(e), "type": type(e).__name__}}))
    sys.exit(1)
"""
