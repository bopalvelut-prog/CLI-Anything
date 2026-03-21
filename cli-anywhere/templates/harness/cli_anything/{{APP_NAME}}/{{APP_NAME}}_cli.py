#!/usr/bin/env python3
"""{{APP_NAME}} CLI — Agent-native interface for {{BINARY}}."""

import sys
import os
import json
import shlex
import click
import functools
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.{{APP_NAME}}.core.session import Session

_session = None
_json_output = False
_repl_mode = False


def get_session():
    global _session
    if _session is None:
        _session = Session()
    return _session


def output(data, message=""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            for k, v in data.items():
                click.echo(f"  {k}: {v}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    click.echo(f"  [{i}]")
                    for k, v in item.items():
                        click.echo(f"    {k}: {v}")
                else:
                    click.echo(f"  - {item}")
        else:
            click.echo(str(data))


def handle_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    return wrapper


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """{{APP_NAME}} CLI — Agent-native interface."""
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command("run")
@click.argument("args", nargs=-1)
@handle_error
def run_cmd(args):
    """Run an arbitrary {{BINARY}} command."""
    import subprocess
    result = subprocess.run(
        ["{{BINARY}}"] + list(args),
        capture_output=True, text=True, timeout=300,
    )
    output({
        "status": "success" if result.returncode == 0 else "error",
        "stdout": result.stdout,
        "stderr": result.stderr,
    })


@cli.command()
@handle_error
def repl():
    """Start interactive REPL."""
    from cli_anything.{{APP_NAME}}.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("{{APP_NAME}}", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    while True:
        try:
            line = skin.get_input(pt_session)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help({})
                continue

            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()

            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


def main():
    cli()


if __name__ == "__main__":
    main()
