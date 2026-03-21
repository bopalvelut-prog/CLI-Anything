#!/usr/bin/env python3
import sys,os,json,shlex,click
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cli_anything.awk.core.session import Session
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
    from cli_anything.awk.utils.repl_skin import ReplSkin
    global _repl_mode;_repl_mode=True
    skin=ReplSkin("awk",version="1.0.0");skin.print_banner()
    pt_session=skin.create_prompt_session()
    while True:
        try:
            line=skin.get_input(pt_session)
            if not line:continue
            if line.lower() in ("quit","exit","q"):skin.print_goodbye();break
            if line.lower()=="help":skin.help({"filter FILE --program P":"Filter with program","filter FILE --field N":"Extract field N","filter FILE --pattern P --action A":"Filter and act","sum FILE --column N":"Sum column","count FILE --pattern P":"Count matches"});continue
            try:args=shlex.split(line)
            except:args=line.split()
            try:cli.main(args,standalone_mode=False)
            except SystemExit:pass
            except click.exceptions.UsageError as e:skin.warning(f"Usage error: {e}")
            except Exception as e:skin.error(f"{e}")
        except (EOFError,KeyboardInterrupt):skin.print_goodbye();break
    _repl_mode=False
@cli.command()
@click.argument("filepath")
@click.option("--program","program",help="AWK program")
@click.option("--field","field",type=int,help="Extract field N")
@click.option("--pattern","pattern",help="Match pattern")
@click.option("--action","action",help="Action on match")
@handle_error
def filter(filepath,program,field,pattern,action):
    from cli_anything.awk.core.text import awk_filter
    result = awk_filter(filepath, program=program, field=field, pattern=pattern, action=action)
    output(result, "Filter results")
@cli.command()
@click.argument("filepath")
@click.option("--column","column",required=True,type=int,help="Column number")
@handle_error
def sum(filepath,column):
    from cli_anything.awk.core.text import awk_sum
    result = awk_sum(filepath, column)
    output(result, f"Sum of column {column}")
@cli.command()
@click.argument("filepath")
@click.option("--pattern","pattern",required=True,help="Pattern to count")
@handle_error
def count(filepath,pattern):
    from cli_anything.awk.core.text import awk_count
    result = awk_count(filepath, pattern)
    output(result, f"Count of '{pattern}'")
def main():cli()
if __name__=="__main__":main()
