#!/usr/bin/env python3
import sys,os,json,shlex,click
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cli_anything.sed.core.session import Session
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
    from cli_anything.sed.utils.repl_skin import ReplSkin
    global _repl_mode;_repl_mode=True
    skin=ReplSkin("sed",version="1.0.0");skin.print_banner()
    pt_session=skin.create_prompt_session()
    while True:
        try:
            line=skin.get_input(pt_session)
            if not line:continue
            if line.lower() in ("quit","exit","q"):skin.print_goodbye();break
            if line.lower()=="help":skin.help({"replace FILE --pattern P --replacement R":"Replace pattern","replace FILE --pattern P --replacement R --inplace":"In-place replace","delete FILE --line N":"Delete line N","insert FILE --line N --text T":"Insert text at line","extract FILE --pattern P":"Extract matching lines"});continue
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
@click.option("--pattern","pattern",required=True,help="Search pattern")
@click.option("--replacement","replacement",required=True,help="Replacement string")
@click.option("--inplace",is_flag=True,help="Edit in place")
@handle_error
def replace(filepath,pattern,replacement,inplace):
    from cli_anything.sed.core.edit import sed_replace
    result = sed_replace(filepath, pattern, replacement, inplace=inplace)
    output(result, "Replace complete")
@cli.command("delete")
@click.argument("filepath")
@click.option("--line","line_num",required=True,type=int,help="Line number to delete")
@handle_error
def delete_cmd(filepath,line_num):
    from cli_anything.sed.core.edit import sed_delete
    result = sed_delete(filepath, line_num)
    output(result, "Deleted")
@cli.command()
@click.argument("filepath")
@click.option("--line","line_num",required=True,type=int,help="Line number")
@click.option("--text","text",required=True,help="Text to insert")
@handle_error
def insert(filepath,line_num,text):
    from cli_anything.sed.core.edit import sed_insert
    result = sed_insert(filepath, line_num, text)
    output(result, "Inserted")
@cli.command()
@click.argument("filepath")
@click.option("--pattern","pattern",required=True,help="Extract pattern")
@handle_error
def extract(filepath,pattern):
    from cli_anything.sed.core.edit import sed_extract
    result = sed_extract(filepath, pattern)
    output(result, "Extracted lines")
def main():cli()
if __name__=="__main__":main()
