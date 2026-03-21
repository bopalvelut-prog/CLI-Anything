#!/usr/bin/env python3
import sys,os,json,shlex,click
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cli_anything.ps.core.session import Session
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
    from cli_anything.ps.utils.repl_skin import ReplSkin
    global _repl_mode;_repl_mode=True
    skin=ReplSkin("ps",version="1.0.0");skin.print_banner()
    pt_session=skin.create_prompt_session()
    while True:
        try:
            line=skin.get_input(pt_session)
            if not line:continue
            if line.lower() in ("quit","exit","q"):skin.print_goodbye();break
            if line.lower()=="help":skin.help({"list":"List processes","list --user USER":"List by user","tree":"Process tree","info --pid PID":"Process info","kill --pid PID":"Kill by PID","kill --name NAME":"Kill by name","top":"Top processes"});continue
            try:args=shlex.split(line)
            except:args=line.split()
            try:cli.main(args,standalone_mode=False)
            except SystemExit:pass
            except click.exceptions.UsageError as e:skin.warning(f"Usage error: {e}")
            except Exception as e:skin.error(f"{e}")
        except (EOFError,KeyboardInterrupt):skin.print_goodbye();break
    _repl_mode=False
@cli.command()
@click.option("--user","user",help="Filter by user")
@handle_error
def list(user):
    from cli_anything.ps.core.process import list_processes
    result = list_processes(user=user)
    output(result, "Processes")
@cli.command()
@handle_error
def tree():
    from cli_anything.ps.core.process import process_tree
    result = process_tree()
    output(result, "Process tree")
@cli.command()
@click.option("--pid","pid",required=True,type=int,help="Process ID")
@handle_error
def info(pid):
    from cli_anything.ps.core.process import process_info
    result = process_info(pid)
    output(result)
@cli.command("kill")
@click.option("--pid","pid",type=int,help="Process ID")
@click.option("--name","name",help="Process name")
@handle_error
def kill_cmd(pid,name):
    from cli_anything.ps.core.process import kill_process
    result = kill_process(pid=pid, name=name)
    output(result, "Kill result")
@cli.command()
@handle_error
def top():
    from cli_anything.ps.core.process import top_processes
    result = top_processes()
    output(result, "Top processes")
def main():cli()
if __name__=="__main__":main()
