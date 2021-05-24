#!/usr/bin/env python
"""
Change Local Git Repo Directory name to RepoName@OrganizationName format
"""
import os
from pathlib import Path
import re
import shutil
import sys

# From Third Party
import click

# From This Project
from giat.giatcfg import gParamDict as gPD

from giat import utils

_ver = "2021.05.22.2618"


def _confirm(p_i: str = "") -> str:
    v = click.prompt(f"{p_i}\nPlease confirm(y/n/A/q)",
                     type=click.Choice(
                         ["y", "yes", "n", "no", "A", "all", "q", "quit"]),
                     show_choices=False,
                     default=gPD["latest_confirm"])

    return utils.unify_confirm(v)


def _in_place(p_i: str = "") -> bool:
    if gPD["need_confirmation_flag"]:
        if (c := _confirm(p_i)) == utils.unify_confirm("yes"):
            gPD["latest_confirm"] = c
            return True
        elif c == utils.unify_confirm("no"):
            gPD["latest_confirm"] = c
            return False
        elif c == utils.unify_confirm("all"):
            gPD["latest_confirm"] = c
            gPD["all_in_place_flag"] = True
            return True
        elif c == utils.unify_confirm("quit"):
            gPD["latest_confirm"] = c
            sys.exit()  # TODO: roughly process ...
    else:
        return False


def _out_info(file: str, new_name: str, take_effect: bool = False) -> None:

    rich_org, rich_proc = utils.rich_style(file, new_name)
    click.echo(" " * 3 + rich_org)
    if take_effect:
        click.echo("==>" + rich_proc)
    else:
        click.echo("-->" + rich_proc)


def _git_config(repo_path: Path):
    config_path = os.path.join(repo_path, ".git/config")
    if not os.path.isfile(config_path):
        return None

    re_pattern_list = [
        ".*github.com/(.*)/(.*).git.*", ".*github.com/(.*)/(.*)"
    ]
    try:
        with open(config_path, "r") as fh:
            for line in fh:
                for rep in re_pattern_list:
                    re_match = re.match(rep, line)
                    if re_match is not None:
                        repo_org = re_match.groups()[0]
                        repo_name = re_match.groups()[1]
                        return repo_name, repo_org

            return None  # run to here ,means no matched configuration found

    except FileNotFoundError as e:
        return None  # run to here,means exception ...


def gitx(repo_path: Path):
    rlt = _git_config(repo_path)
    if not (new_repo_name :=
            None if rlt is None else str(rlt[0]) + "@" + str(rlt[1])):
        return None

    current_repo_name = str(os.path.realpath(repo_path)).rstrip(
        os.path.sep).split(os.path.sep)[-1]
    repo_dir_path = os.path.sep.join(
        str(repo_path).rstrip(os.path.sep).split(os.path.sep)[:-1])
    current_repo_path = os.path.join(repo_dir_path, current_repo_name)
    new_repo_path = os.path.join(repo_dir_path, new_repo_name)
    if os.path.realpath(current_repo_path) == os.path.realpath(new_repo_path):
        return None

    _ap = gPD["absolute_path_flag"]

    if _ap:
        ip = _in_place(os.path.abspath(current_repo_path))
    else:
        ip = _in_place(str(current_repo_path))
    if ip:
        if os.path.exists(new_repo_path):
            click.echo(f"{new_repo_path} exist.\n"
                       f"{current_repo_path} Skipped.")
            return None

        else:
            pass
            os.replace(current_repo_path,
                       new_repo_path)  # os.place is atomic and match
            # cross platform :https://docs.python.org/dev/library/os.html
    if _ap:
        _out_info(str(os.path.abspath(current_repo_path)),
                  str(os.path.abspath(new_repo_path)),
                  take_effect=ip)
    else:
        _out_info(str(current_repo_path), str(new_repo_path), take_effect=ip)

    gPD["target_appeared"] = True


# TODO:add only display mode such as display all local git repo
@click.command(
    context_settings={
        "ignore_unknown_options": True,
        "help_option_names": ["-h", "--help"],
        "max_content_width": shutil.get_terminal_size()[0]
    })
@click.argument("path", required=False, type=click.Path(exists=True), nargs=-1)
@click.option("--max-depth",
              "-d",
              default=1,
              type=int,
              help=f"Set travel directory tree with max depth.",
              show_default=True)
@click.option("--confirm",
              "-c",
              default=False,
              type=bool,
              is_flag=True,
              help=f"Need confirmation before change to take effect.",
              show_default=True)
@click.option("--absolute-path",
              "-a",
              default=False,
              type=bool,
              is_flag=True,
              help=f"Show absolute path of file.",
              show_default=True)
@click.version_option(version=_ver)
def giat(path, max_depth, confirm, absolute_path):
    if not path:
        gPD["path"] = ["."]
    else:
        gPD["path"] = path
    gPD["max_depth"] = max_depth
    gPD["need_confirmation_flag"] = confirm
    gPD["absolute_path_flag"] = absolute_path
    gPD["all_in_place_flag"] = False
    gPD["latest_confirm"] = utils.unify_confirm(
    )  # Parameter is Null to get default return
    gPD["target_appeared"] = False
    for pth in gPD["path"]:
        if not os.path.isdir(pth):
            continue
        for root, subdir, files in utils.depth_walk(
                pth, max_depth=gPD["max_depth"]):
            if ".git" in subdir:
                gitx(root)
    # Print some tips at last
    if (not gPD["need_confirmation_flag"]) and (gPD["target_appeared"]):
        cols, _ = shutil.get_terminal_size(fallback=(79, 23))
        click.echo("*" * cols)
        click.echo("In order to take effect,add option '-c'")
        gPD["target_appeared"] = False
