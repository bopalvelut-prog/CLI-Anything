#!/usr/bin/env python3
import sys,os,json,shlex,click
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cli_anything.find.core.session import Session
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
    from cli_anything.find.utils.repl_skin import ReplSkin
    global _repl_mode;_repl_mode=True
    skin=ReplSkin("find",version="1.0.0");skin.print_banner()
    pt_session=skin.create_prompt_session()
    while True:
        try:
            line=skin.get_input(pt_session)
            if not line:continue
            if line.lower() in ("quit","exit","q"):skin.print_goodbye();break
            if line.lower()=="help":skin.help({"search --path P --name PATTERN":"Search by name","search --path P --type f|d":"Search by type","search --path P --size +N":"Search by size","search --path P --mtime N":"Search by modification time","search --path P --exec CMD":"Search and execute","search --path P --user U":"Search by user"});continue
            try:args=shlex.split(line)
            except:args=line.split()
            try:cli.main(args,standalone_mode=False)
            except SystemExit:pass
            except click.exceptions.UsageError as e:skin.warning(f"Usage error: {e}")
            except Exception as e:skin.error(f"{e}")
        except (EOFError,KeyboardInterrupt):skin.print_goodbye();break
    _repl_mode=False
@cli.command()
@click.option("--path","search_path",required=True,help="Search path")
@click.option("--name","pattern",help="Name pattern")
@click.option("--type","file_type",help="File type (f or d)")
@click.option("--size","size",help="Size filter (+N or -N)")
@click.option("--mtime","mtime",help="Modification time days")
@click.option("--exec","exec_cmd",help="Execute command on results")
@click.option("--user","user",help="Filter by user")
@handle_error
def search(search_path,pattern,file_type,size,mtime,exec_cmd,user):
    from cli_anything.find.core.search import run_search
    result = run_search(search_path, name=pattern, file_type=file_type, size=size, mtime=mtime, exec_cmd=exec_cmd, user=user)
    output(result, "Search results")
def main():cli()
if __name__=="__main__":main()
