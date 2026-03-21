#!/usr/bin/env python3
"""
cli-anything — Install and manage CLI harnesses for any software.

Usage:
    cli-anything install <app>        Install a harness
    cli-anything install gimp blender  Install multiple
    cli-anything list                  List available harnesses
    cli-anything search <query>        Search harnesses
    cli-anything doctor                Check prerequisites
    cli-anything run <app> [args]      Run a harness
    cli-anything new <app>             Create new harness from template
"""

import sys
import os
import json
import subprocess
import argparse
import shutil
from pathlib import Path

REPO = "HKUDS/CLI-Anything"
BRANCH = "feat/vlc-freecad"
REGISTRY_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/registry.json"
CONFIG_DIR = Path.home() / ".config" / "cli-anything"
HARNESS_DIR = CONFIG_DIR / "harnesses"
COMMANDS_DIR = CONFIG_DIR / "commands"

# Top harnesses that provide real value (GUI apps with no native CLI)
RECOMMENDED = [
    "gimp",
    "blender",
    "inkscape",
    "libreoffice",
    "kdenlive",
    "obs-studio",
    "audacity",
    "shotcut",
    "zoom",
    "comfyui",
    "drawio",
    "mermaid",
    "vlc",
    "freecad",
    "krita",
    "darktable",
    "scribus",
    "kicad",
    "ghidra",
    "godot",
    "imagemagick",
    "sox",
    "ffprobe",
    "gpg",
    "docker",
    "git",
    "ffmpeg",
    "pandoc",
    "tesseract",
    "terraform",
]


def main():
    parser = argparse.ArgumentParser(
        prog="cli-anything",
        description="Install and manage CLI harnesses for any software",
    )
    sub = parser.add_subparsers(dest="command")

    # install
    p_install = sub.add_parser("install", help="Install harness(es)")
    p_install.add_argument("apps", nargs="+", help="App name(s) or 'recommended'")

    # list
    sub.add_parser("list", help="List available harnesses")

    # search
    p_search = sub.add_parser("search", help="Search harnesses")
    p_search.add_argument("query", help="Search query")

    # doctor
    sub.add_parser("doctor", help="Check prerequisites")

    # run
    p_run = sub.add_parser("run", help="Run a harness")
    p_run.add_argument("app", help="App name")
    p_run.add_argument("args", nargs="*", help="Arguments")

    # new
    p_new = sub.add_parser("new", help="Create new harness from template")
    p_new.add_argument("app", help="App name")
    p_new.add_argument("--binary", help="Binary name (default: same as app)")

    args = parser.parse_args()

    if args.command == "install":
        cmd_install(args.apps)
    elif args.command == "list":
        cmd_list()
    elif args.command == "search":
        cmd_search(args.query)
    elif args.command == "doctor":
        cmd_doctor()
    elif args.command == "run":
        cmd_run(args.app, args.args)
    elif args.command == "new":
        cmd_new(args.app, getattr(args, "binary", None))
    else:
        parser.print_help()


def cmd_install(apps):
    """Install harness(es)."""
    if apps == ["recommended"]:
        apps = RECOMMENDED

    registry = fetch_registry()
    installed = []

    for app in apps:
        entry = find_in_registry(registry, app)
        if entry:
            install_from_registry(entry)
            installed.append(app)
        else:
            print(f"  ⚠ {app} not found in registry, trying direct install...")
            install_direct(app)
            installed.append(app)

    print(f"\n✅ Installed {len(installed)} harness(es): {', '.join(installed)}")
    print(f"\nCommands available in: {COMMANDS_DIR}")
    print(f'Add to PATH: export PATH="{COMMANDS_DIR}:$PATH"')


def cmd_list():
    """List available harnesses."""
    registry = fetch_registry()
    categories = {}
    for entry in registry.get("clis", []):
        cat = entry.get("category", "other")
        categories.setdefault(cat, []).append(entry["name"])

    for cat in sorted(categories):
        print(f"\n  [{cat}]")
        for name in sorted(categories[cat]):
            marker = "✓" if is_installed(name) else " "
            print(f"    {marker} {name}")

    total = len(registry.get("clis", []))
    installed = sum(1 for e in registry.get("clis", []) if is_installed(e["name"]))
    print(f"\n  {installed}/{total} installed")


def cmd_search(query):
    """Search harnesses."""
    registry = fetch_registry()
    q = query.lower()
    matches = [
        e
        for e in registry.get("clis", [])
        if q in e["name"].lower() or q in e.get("description", "").lower()
    ]
    for e in matches[:20]:
        status = "✓" if is_installed(e["name"]) else " "
        print(f"  {status} {e['name']}: {e.get('description', '')[:60]}")


def cmd_doctor():
    """Check prerequisites."""
    print("  Checking prerequisites...\n")
    checks = [
        ("Python 3.10+", sys.version_info >= (3, 10)),
        ("pip", shutil.which("pip") is not None),
        ("git", shutil.which("git") is not None),
        ("click", try_import("click")),
        ("prompt-toolkit", try_import("prompt_toolkit")),
    ]
    for name, ok in checks:
        print(f"  {'✅' if ok else '❌'} {name}")

    # Check common binaries
    print("\n  Software binaries:")
    for app in ["gimp", "blender", "inkscape", "vlc", "ffmpeg", "git", "docker"]:
        found = shutil.which(app)
        print(f"  {'✅' if found else '❌'} {app}: {found or 'not found'}")


def cmd_run(app, args):
    """Run a harness."""
    cmd_name = f"cli-anything-{app}"
    cmd_path = COMMANDS_DIR / cmd_name

    if not cmd_path.exists():
        # Try as a Python module
        try:
            subprocess.run(
                [sys.executable, "-m", f"cli_anything.{app}.{app}_cli"] + args,
                check=True,
            )
            return
        except (subprocess.CalledProcessError, ModuleNotFoundError):
            print(
                f"  ❌ Harness '{app}' not installed. Run: cli-anything install {app}"
            )
            sys.exit(1)

    subprocess.run([str(cmd_path)] + args)


def cmd_new(app, binary=None):
    """Create new harness from template."""
    binary = binary or app
    template_dir = Path(__file__).parent.parent / "templates" / "harness"
    target_dir = HARNESS_DIR / app

    if target_dir.exists():
        print(f"  ⚠ {app} already exists at {target_dir}")
        return

    print(f"  Creating harness for {app} (binary: {binary})...")
    shutil.copytree(template_dir, target_dir, dirs_exist_ok=True)

    # Replace placeholders
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            fp = Path(root) / f
            content = fp.read_text()
            content = content.replace("{{APP_NAME}}", app)
            content = content.replace("{{BINARY}}", binary)
            fp.write_text(content)

    print(f"  ✅ Created at {target_dir}")
    print(f"  Edit the files, then: pip install -e {target_dir}/agent-harness")


def fetch_registry():
    """Fetch the registry from GitHub."""
    cache = CONFIG_DIR / "registry.json"
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if cache.exists() and (
        os.path.getmtime(str(cache)) > os.path.getmtime(str(__file__))
    ):
        return json.loads(cache.read_text())

    try:
        import urllib.request

        with urllib.request.urlopen(REGISTRY_URL, timeout=10) as resp:
            data = json.loads(resp.read())
            cache.write_text(json.dumps(data, indent=2))
            return data
    except Exception:
        if cache.exists():
            return json.loads(cache.read_text())
        return {"clis": []}


def find_in_registry(registry, name):
    """Find an entry in the registry."""
    for entry in registry.get("clis", []):
        if entry["name"] == name:
            return entry
    return None


def is_installed(name):
    """Check if a harness is installed."""
    return (COMMANDS_DIR / f"cli-anything-{name}").exists() or (
        HARNESS_DIR / name
    ).exists()


def install_from_registry(entry):
    """Install a harness from registry."""
    name = entry["name"]
    HARNESS_DIR.mkdir(parents=True, exist_ok=True)
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"  Installing {name}...")

    # Install via pip
    install_cmd = entry.get("install_cmd", "")
    if "git+" in install_cmd:
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    install_cmd,
                    "--quiet",
                    "--break-system-packages",
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    install_cmd,
                    "--quiet",
                    "--user",
                ],
                check=True,
                capture_output=True,
            )

    # Create symlink to command
    entry_point = entry.get("entry_point", f"cli-anything-{name}")
    cmd_src = shutil.which(entry_point)
    if cmd_src:
        cmd_dst = COMMANDS_DIR / entry_point
        if not cmd_dst.exists():
            cmd_dst.symlink_to(cmd_src)


def install_direct(name):
    """Direct install from GitHub."""
    url = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.zip"
    subdir = f"{name}/agent-harness"
    HARNESS_DIR.mkdir(parents=True, exist_ok=True)
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"git+https://github.com/{REPO}.git#subdirectory={subdir}",
                "--quiet",
                "--break-system-packages",
            ],
            check=True,
            capture_output=True,
        )
        print(f"  ✅ {name} installed")
    except subprocess.CalledProcessError:
        print(f"  ❌ Failed to install {name}")


def try_import(module):
    """Try importing a module."""
    try:
        __import__(module)
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    main()
