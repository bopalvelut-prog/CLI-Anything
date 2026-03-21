"""Node version management using nvm."""
import subprocess,os

def _nvm_cmd(args):
    nvm_dir = os.environ.get("NVM_DIR", os.path.expanduser("~/.nvm"))
    script = f'source {nvm_dir}/nvm.sh && nvm {" ".join(args)}'
    result = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=30)
    return result

def list_versions():
    result = _nvm_cmd(["ls"])
    lines = result.stdout.strip().split("\n")
    versions = [l.strip().replace("->","").strip() for l in lines if l.strip() and "v" in l]
    return {"installed": versions}

def list_remote_versions():
    result = _nvm_cmd(["ls-remote", "--lts"])
    lines = result.stdout.strip().split("\n")[-10:]
    return {"remote": [l.strip() for l in lines if l.strip()]}

def install_version(version):
    result = _nvm_cmd(["install", version])
    return {"installed": version, "output": result.stdout[-500:]}

def use_version(version):
    return {"info": f"Run: nvm use {version} (shell-specific, use 'source' method)"}

def uninstall_version(version):
    result = _nvm_cmd(["uninstall", version])
    return {"uninstalled": version, "output": result.stdout[-500:]}

def current_version():
    result = _nvm_cmd(["current"])
    return {"current": result.stdout.strip()}

def create_alias(name, version):
    result = _nvm_cmd(["alias", name, version])
    return {"alias": name, "version": version, "output": result.stdout.strip()}

def which_version(version):
    result = _nvm_cmd(["which", version])
    return {"version": version, "path": result.stdout.strip()}
