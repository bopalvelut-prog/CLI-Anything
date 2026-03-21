"""Ansible Galaxy role management."""
import subprocess

def search_roles(query):
    cmd = ["ansible-galaxy", "search", query]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return {"query": query, "results": result.stdout.strip().split("\n")[:20]}

def role_info(role):
    cmd = ["ansible-galaxy", "info", role]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return {"role": role, "info": result.stdout.strip()[:2000]}

def install_role(role):
    cmd = ["ansible-galaxy", "install", role]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return {"installed": role, "returncode": result.returncode, "output": result.stdout[-500:]}

def init_role(role_name):
    cmd = ["ansible-galaxy", "init", role_name]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return {"initialized": role_name, "returncode": result.returncode}

def list_roles():
    cmd = ["ansible-galaxy", "list"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    roles = [r.strip() for r in result.stdout.strip().split("\n") if r.strip()]
    return {"roles": roles, "count": len(roles)}

def remove_role(role):
    import os
    path = os.path.expanduser(f"~/.ansible/roles/{role}")
    if os.path.exists(path):
        import shutil
        shutil.rmtree(path)
        return {"removed": role}
    return {"error": f"Role {role} not found at {path}"}

def install_collection(name):
    cmd = ["ansible-galaxy", "collection", "install", name]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return {"installed": name, "returncode": result.returncode, "output": result.stdout[-500:]}
