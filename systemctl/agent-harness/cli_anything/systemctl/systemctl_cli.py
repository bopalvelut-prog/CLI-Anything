#!/usr/bin/env python3
import sys,os,json,shlex,click
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cli_anything.systemctl.core.session import Session
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
    from cli_anything.systemctl.utils.repl_skin import ReplSkin
    global _repl_mode;_repl_mode=True
    skin=ReplSkin("systemctl",version="1.0.0");skin.print_banner()
    pt_session=skin.create_prompt_session()
    while True:
        try:
            line=skin.get_input(pt_session)
            if not line:continue
            if line.lower() in ("quit","exit","q"):skin.print_goodbye();break
            if line.lower()=="help":skin.help({"status --service S":"Service status","start --service S":"Start service","stop --service S":"Stop service","restart --service S":"Restart service","enable --service S":"Enable service","disable --service S":"Disable service","list-units":"List units","list-units --type TYPE":"List by type","journal --service S":"Show journal","mask --service S":"Mask service","reload --service S":"Reload service"});continue
            try:args=shlex.split(line)
            except:args=line.split()
            try:cli.main(args,standalone_mode=False)
            except SystemExit:pass
            except click.exceptions.UsageError as e:skin.warning(f"Usage error: {e}")
            except Exception as e:skin.error(f"{e}")
        except (EOFError,KeyboardInterrupt):skin.print_goodbye();break
    _repl_mode=False
@cli.command()
@click.option("--service","service",required=True,help="Service name")
@handle_error
def status(service):
    from cli_anything.systemctl.core.services import service_status
    result = service_status(service)
    output(result)
@cli.command()
@click.option("--service","service",required=True,help="Service name")
@handle_error
def start(service):
    from cli_anything.systemctl.core.services import start_service
    result = start_service(service)
    output(result, f"Started {service}")
@cli.command()
@click.option("--service","service",required=True,help="Service name")
@handle_error
def stop(service):
    from cli_anything.systemctl.core.services import stop_service
    result = stop_service(service)
    output(result, f"Stopped {service}")
@cli.command()
@click.option("--service","service",required=True,help="Service name")
@handle_error
def restart(service):
    from cli_anything.systemctl.core.services import restart_service
    result = restart_service(service)
    output(result, f"Restarted {service}")
@cli.command()
@click.option("--service","service",required=True,help="Service name")
@handle_error
def enable(service):
    from cli_anything.systemctl.core.services import enable_service
    result = enable_service(service)
    output(result, f"Enabled {service}")
@cli.command()
@click.option("--service","service",required=True,help="Service name")
@handle_error
def disable(service):
    from cli_anything.systemctl.core.services import disable_service
    result = disable_service(service)
    output(result, f"Disabled {service}")
@cli.command("list-units")
@click.option("--type","unit_type",help="Unit type filter")
@handle_error
def list_units(unit_type):
    from cli_anything.systemctl.core.services import list_units
    result = list_units(unit_type=unit_type)
    output(result, "Units")
@cli.command()
@click.option("--service","service",required=True,help="Service name")
@click.option("--lines","lines",default=50,type=int,help="Number of lines")
@handle_error
def journal(service,lines):
    from cli_anything.systemctl.core.services import show_journal
    result = show_journal(service, lines=lines)
    output(result, f"Journal for {service}")
@cli.command()
@click.option("--service","service",required=True,help="Service name")
@handle_error
def mask(service):
    from cli_anything.systemctl.core.services import mask_service
    result = mask_service(service)
    output(result, f"Masked {service}")
@cli.command()
@click.option("--service","service",required=True,help="Service name")
@handle_error
def reload(service):
    from cli_anything.systemctl.core.services import reload_service
    result = reload_service(service)
    output(result, f"Reloaded {service}")
def main():cli()
if __name__=="__main__":main()
