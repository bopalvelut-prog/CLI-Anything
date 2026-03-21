#!/usr/bin/env python3
import sys,os,json,shlex,click
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cli_anything.nvm.core.session import Session
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
    from cli_anything.nvm.utils.repl_skin import ReplSkin
    global _repl_mode;_repl_mode=True
    skin=ReplSkin("nvm",version="1.0.0");skin.print_banner()
    pt_session=skin.create_prompt_session()
    while True:
        try:
            line=skin.get_input(pt_session)
            if not line:continue
            if line.lower() in ("quit","exit","q"):skin.print_goodbye();break
            if line.lower()=="help":skin.help({"list":"List installed versions","list-remote":"List remote versions","install --version V":"Install version","use --version V":"Use version","uninstall --version V":"Uninstall version","current":"Current version","alias --name N --version V":"Create alias","which --version V":"Show path"});continue
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
    from cli_anything.nvm.core.versions import list_versions
    result = list_versions()
    output(result, "Installed versions")
@cli.command("list-remote")
@handle_error
def list_remote():
    from cli_anything.nvm.core.versions import list_remote_versions
    result = list_remote_versions()
    output(result, "Remote versions")
@cli.command()
@click.option("--version","version",required=True,help="Node version")
@handle_error
def install(version):
    from cli_anything.nvm.core.versions import install_version
    result = install_version(version)
    output(result, f"Installed {version}")
@cli.command()
@click.option("--version","version",required=True,help="Node version")
@handle_error
def use(version):
    from cli_anything.nvm.core.versions import use_version
    result = use_version(version)
    output(result, f"Using {version}")
@cli.command()
@click.option("--version","version",required=True,help="Node version")
@handle_error
def uninstall(version):
    from cli_anything.nvm.core.versions import uninstall_version
    result = uninstall_version(version)
    output(result, f"Uninstalled {version}")
@cli.command()
@handle_error
def current():
    from cli_anything.nvm.core.versions import current_version
    result = current_version()
    output(result, "Current version")
@cli.command()
@click.option("--name","name",required=True,help="Alias name")
@click.option("--version","version",required=True,help="Node version")
@handle_error
def alias(name,version):
    from cli_anything.nvm.core.versions import create_alias
    result = create_alias(name, version)
    output(result, f"Alias {name} -> {version}")
@cli.command()
@click.option("--version","version",required=True,help="Node version")
@handle_error
def which(version):
    from cli_anything.nvm.core.versions import which_version
    result = which_version(version)
    output(result, f"Path for {version}")
def main():cli()
if __name__=="__main__":main()
