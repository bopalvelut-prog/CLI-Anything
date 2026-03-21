#!/usr/bin/env python3
import sys,os,json,shlex,click
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cli_anything.screen.core.session import Session
_session=None;_json_output=False;_repl_mode=False
def get_session():
    global _session
    if _session is None:_session=Session()
    return _session
def output(data,message=""):
    if _json_output:click.echo(json.dumps(data,indent=2,default=str))
    else:
        if message:click.echo(message)
        if isinstance(data,dict):
            for k,v in data.items():click.echo(f"  {k}: {v}")
        elif isinstance(data,list):
            for i,item in enumerate(data):
                if isinstance(item,dict):
                    click.echo(f"  [{i}]")
                    for k,v in item.items():click.echo(f"    {k}: {v}")
                else:click.echo(f"  - {item}")
        else:click.echo(str(data))
def handle_error(func):
    def wrapper(*args,**kwargs):
        try:return func(*args,**kwargs)
        except Exception as e:
            if _json_output:click.echo(json.dumps({"error":str(e),"type":type(e).__name__}))
            else:click.echo(f"Error: {e}",err=True)
            if not _repl_mode:sys.exit(1)
    wrapper.__name__=func.__name__;wrapper.__doc__=func.__doc__;return wrapper
@click.group(invoke_without_command=True)
@click.option("--json","use_json",is_flag=True)
@click.pass_context
def cli(ctx,use_json):
    global _json_output;_json_output=use_json
    if ctx.invoked_subcommand is None:ctx.invoke(repl)
@cli.command()
@handle_error
def repl():
    from cli_anything.screen.utils.repl_skin import ReplSkin
    global _repl_mode;_repl_mode=True
    skin=ReplSkin("screen",version="1.0.0");skin.print_banner()
    pt_session=skin.create_prompt_session()
    while True:
        try:
            line=skin.get_input(pt_session)
            if not line:continue
            if line.lower() in ("quit","exit","q"):skin.print_goodbye();break
            if line.lower()=="help":skin.help({"list":"List sessions","create --name N":"Create session","attach --name N":"Attach to session","detach --name N":"Detach session","kill --name N":"Kill session","send --name N --cmd CMD":"Send command"});continue
            try:args=shlex.split(line)
            except:args=line.split()
            try:cli.main(args,standalone_mode=False)
            except SystemExit:pass
            except click.exceptions.UsageError as e:skin.warning(f"Usage error: {e}")
            except Exception as e:skin.error(f"{e}")
        except (EOFError,KeyboardInterrupt):skin.print_goodbye();break
    _repl_mode=False
@cli.command()
@handle_error
def list():
    from cli_anything.screen.core.terminal import list_sessions
    result = list_sessions()
    output(result, "Screen sessions")
@cli.command()
@click.option("--name","name",required=True,help="Session name")
@handle_error
def create(name):
    from cli_anything.screen.core.terminal import create_session
    result = create_session(name)
    output(result, f"Created session {name}")
@cli.command()
@click.option("--name","name",required=True,help="Session name")
@handle_error
def attach(name):
    from cli_anything.screen.core.terminal import attach_session
    result = attach_session(name)
    output(result, f"Attached to {name}")
@cli.command()
@click.option("--name","name",required=True,help="Session name")
@handle_error
def detach(name):
    from cli_anything.screen.core.terminal import detach_session
    result = detach_session(name)
    output(result, f"Detached {name}")
@cli.command()
@click.option("--name","name",required=True,help="Session name")
@handle_error
def kill(name):
    from cli_anything.screen.core.terminal import kill_session
    result = kill_session(name)
    output(result, f"Killed session {name}")
@cli.command()
@click.option("--name","name",required=True,help="Session name")
@click.option("--cmd","command",required=True,help="Command to send")
@handle_error
def send(name,command):
    from cli_anything.screen.core.terminal import send_command
    result = send_command(name, command)
    output(result, f"Sent to {name}")
def main():cli()
if __name__=="__main__":main()
