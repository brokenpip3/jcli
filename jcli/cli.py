#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from api4jenkins import Jenkins, exceptions
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print
from time import sleep
from sys import exit

# from .config import load_and_validate, setup_config
from .config import load_and_validate, setup_config
from .version import __version__

console = Console()
error = Console(stderr=True, style="bold red")


def init_server_connection(url, user, password):
    """
    Init jenkins server connection
    """
    try:
        s = Jenkins(url, auth=(user, password))
        s.version
        global server
        server = s
    except exceptions.AuthenticationError as e:
        print(e)
        exit(1)


def get_server_info(a: bool):
    """
    Grab various server info
    """
    if a:
        print(f"version: {str(server.version)}")
        infos = ["nodeDescription", "useCrumbs", "useSecurity"]
        for i in infos:
            print(f"{i}: {server.api_json()[i]}")
    else:
        print(server.version)


def job_health_check(value: int):
    """
    Check health by value according to:
    https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/HealthReport.java
    and output the corresponding icon
    """
    if value >= 80:
        return ":sunny:"
    elif 79 <= value <= 39:
        return ":loud_with_rain:"
    else:
        return ":fire:"


def job_get_all(deep: int):
    """
    Iterate over folders and print list of jobs
    deep: how deep we need to iterate
    """
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Name", style="dim")
    table.add_column("Description")
    table.add_column("Folder")
    table.add_column("Builds")
    table.add_column("Health")
    with console.status("[bold green]Scraping all jobs, please wait...") as status:
        for job in server.iter_jobs(deep):
            # name = job.__class__.__name__
            jtypes = ["hudson.model.FreeStyleProject", "org.jenkinsci.plugins.workflow.job.WorkflowJob"]
            if job._class in jtypes:
                status.update(f"[green]Job found: [bold green]{job.display_name}[/bold green], processing..")
                _jname = job.display_name
                _jfulln = str(job.api_json()["fullName"])
                _jdir = _jfulln.split("/")[0] if "/" in _jfulln else ""
                _jdesc = job.description
                _jlastb = str(job.api_json()["lastBuild"]["number"])
                _jhealth = job.api_json()["healthReport"][0]["score"]
                table.add_row(_jname, _jdesc, _jdir, _jlastb, job_health_check(_jhealth))
        status.update("[bold green]Done!")
        console.print(table)


def job_exist(name: str) -> bool:
    """
    Check if job exist
    """
    try:
        if server[name].exists():
            return True
    except AttributeError:
        error.print(":exclamation:  [bold red]No job named {name} found, exit.")
        exit(1)


def job_parameters(job: str) -> bool | dict:
    """
    Check if job has parameters
    """
    params = {}
    j = server[job].api_json()["property"]
    if not j:
        return False
    else:
        for p in j:
            if "parameterDefinitions" in p:
                for parameter in p["parameterDefinitions"]:
                    params[parameter["defaultParameterValue"]["name"]] = parameter["defaultParameterValue"]["value"]
                return params


def build_job(name: str, param: dict):
    if job_exist(name):
        item = server.build_job(name, **param)
        with console.status("[bold green]Waiting for job queue..") as status:
            while not item.get_build():
                sleep(0.5)
            build = item.get_build()
            status.update("[bold green blink]Grabbing logs..")
            console.clear()
            for line in build.progressive_output():
                console.print(line, markup=False, highlight=False)
            console.print(f"Job url: {build.url}")


def job_checks(name: str):
    """
    Check if the job has parameters
    and ask to insert them printing
    the default value
    """
    p = job_parameters(name)
    new_param = {}
    if p:
        ask = Confirm.ask(
            f"Job [bold green] {name} [/bold green] has parameters, do you want to insert them?", default=True
        )
        if ask:
            for k, v in p.items():
                t = Prompt.ask(f"{k}", default=f"{v}")
                new_param[k] = t
            return new_param
    else:
        ask = Confirm.ask(
            f"Job [bold green] {name} [/bold green] has no parameters, do you want to proceed?", default=True
        )
        if ask:
            return new_param
        else:
            exit(0)


@click.group(help="jcli - Jenkins job cli")
@click.version_option(__version__)
def main():
    pass


@main.command(help="Create jcli config")
def config():
    setup_config()


@main.group(help="Get Jenkins server info")
@click.pass_context
def jenkins(ctx):
    pass


@jenkins.command(help="Get server version", name="version")
def version():
    cfg = load_and_validate()
    init_server_connection(cfg["server"], cfg["user"], cfg["password"])
    get_server_info(a=False)


@jenkins.command(help="Get generic info", name="info")
def info():
    cfg = load_and_validate()
    init_server_connection(cfg["server"], cfg["user"], cfg["password"])
    get_server_info(a=True)


@main.group(help="List and execute jobs")
@click.pass_context
def jobs(ctx):
    pass


@jobs.command(help="Run jenkins jobs", name="run")
@click.argument("name", envvar="JCLI_JOB", nargs=1)
# https://click.palletsprojects.com/en/8.0.x/complex/
@click.pass_context
def run(ctx, name):
    cfg = load_and_validate()
    init_server_connection(cfg["server"], cfg["user"], cfg["password"])
    param = job_checks(name)
    ctx.obj = build_job(name, param)


@jobs.command(help="List jenkins jobs", name="list")
@click.option("--deep")
# https://click.palletsprojects.com/en/8.0.x/complex/
@click.pass_context
def list(ctx, deep):
    _d = 1
    cfg = load_and_validate()
    init_server_connection(cfg["server"], cfg["user"], cfg["password"])
    if deep:
        _d = deep
    ctx.obj = job_get_all(_d)


if __name__ == "__main__":
    main()
