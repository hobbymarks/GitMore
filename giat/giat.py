#!/usr/bin/env python
import click


# TODO: split rich style to standalone
def rich_style(org_str="", pro_str=""):
    """
    Compare original string and processed string ,
    return difference with rich style
    delete decorated by bold red
    add decorated by bold green
    space decorated by square box
    :param org_str: short for original string
    :param pro_str: short for processed string
    :return: riched original string and riched processed string
    *riched means decorated by rich package
    """
    global gParamDict
    import difflib
    rich_org_str = rich_pro_str = ""
    rich_org_dif_pos = rich_pro_dif_pos = 0
    for match in difflib.SequenceMatcher(None, org_str,
                                         pro_str).get_matching_blocks():
        if rich_org_dif_pos < match.a:
            rich_org_str += "[bold red]" + org_str[
                rich_org_dif_pos:match.a].replace(
                    " ", "▯") + "[/bold red]" + org_str[match.a:match.a +
                                                        match.size]
            rich_org_dif_pos = match.a + match.size
        else:
            rich_org_str += org_str[match.a:match.a + match.size]
            rich_org_dif_pos = match.a + match.size

        if rich_pro_dif_pos < match.b:
            rich_pro_str += "[bold green]" + pro_str[
                rich_pro_dif_pos:match.b].replace(
                    " ", "▯") + "[/bold green]" + pro_str[match.b:match.b +
                                                          match.size]
            rich_pro_dif_pos = match.b + match.size
        else:
            rich_pro_str += pro_str[match.b:match.b + match.size]
            rich_pro_dif_pos = match.b + match.size

    return rich_org_str, rich_pro_str


def get_git_config(git_repo_path=None):
    """
    retrieve git configuration by from given local git repo path
    :param git_repo_path: git repo path
    :return: git repo name  and org name
    """
    import logging
    logger = logging.getLogger("giat")
    # TODO: decorate logger by rich
    global gParamDict
    import os
    import re
    if git_repo_path is None:
        logger.warning(f"git repo path is None:{git_repo_path}")
        return None
    if not os.path.exists(git_repo_path):
        logger.warning(f"git repo path not exist:{git_repo_path}")
        return None
    if not os.path.isdir(os.path.join(git_repo_path, ".git")):
        logger.warning(f"No valid directory found:{git_repo_path}")
        return None
    config_path = os.path.join(git_repo_path, ".git/config")
    if not os.path.isfile(config_path):
        logger.warning(f"No valid configuration file found:{git_repo_path}")
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
                        logger.debug(
                            f"read git config successfully:{config_path}")
                        return re_match.groups()
            logger.warning(f"No matched configuration found:{config_path}")
            return None  # run to here ,means no matched configuration found
    except FileNotFoundError:
        logger.error(f"read file failed:{config_path}")

    return None  #run to here,means exception ...


def gitx(git_repo_path=None):
    """
    Change local git repo dir name to git@org style
    :param git_repo_path: local git repo path
    :return:
    """
    import logging
    logger = logging.getLogger("giat")
    global gParamDict

    if git_repo_path is not None:
        result = get_git_config(git_repo_path)
    else:
        logger.warning(f"git repo path is None:{git_repo_path}")
        return None
    new_repo_name = None if result is None else str(result[1]) + "@" + str(
        result[0])
    if new_repo_name is None:
        logger.warning(f"Not got valid configuration:{git_repo_path}")
        return None
    import os
    current_repo_name = str(git_repo_path).rstrip(os.path.sep).split(
        os.path.sep)[-1]
    current_repo_dir_path = os.path.sep.join(
        str(git_repo_path).rstrip(os.path.sep).split(os.path.sep)[:-1])
    current_repo_path = os.path.join(current_repo_dir_path, current_repo_name)
    new_repo_path = os.path.join(current_repo_dir_path, new_repo_name)
    if current_repo_path == new_repo_path:
        logger.debug(f"No Need giat:{current_repo_path}")
        return None
    if not gParamDict["dry_run"]:
        try:
            os.rename(current_repo_path, new_repo_path)
            logger.debug(
                f"rename {current_repo_name} to {new_repo_name} successfully.")
        except IOError:
            logger.warning(
                f"rename {current_repo_name} to {new_repo_name} failed.")
        else:
            e = sys.exc_info()
            logger.warning(e)

    console, style = gParamDict["console"]
    rich_current_repo_path, rich_new_repo_path = rich_style(
        current_repo_path, new_repo_path)
    console.print(" " * 3 + rich_current_repo_path, style=style)
    if gParamDict["dry_run"]:
        console.print("-->" + rich_new_repo_path, style=style)
    else:
        console.print("==>" + rich_new_repo_path, style=style)


# TODO:add only display mode such as diplay all local git repo
@click.command(context_settings={"ignore_unknown_options": True})
@click.option("-v", "--verbose", count=True, help="Enables verbose mode.")
@click.argument("dir_path", required=False, type=click.Path(exists=True))
@click.option("-d",
              "--dry_run",
              default=True,
              type=bool,
              help="If dry_run is True will not change file name.",
              show_default=True)
def giat(verbose, dir_path, dry_run):
    """
    traverse all directory and sub directory then
    change git local repo directory name to RepoName@OrgName format
    :param dir_path:
    :param dry_run:
    :return:

    """
    import logging
    logger = logging.getLogger("giat")
    global gParamDict
    if dir_path:
        gParamDict["dir_path"] = dir_path
    else:
        gParamDict["dir_path"] = "."
    gParamDict["dry_run"] = dry_run
    if verbose == 1:
        gParamDict["verbose"] = 1
        logger.handlers[1].setLevel(logging.ERROR)
    elif verbose == 2:
        gParamDict["verbose"] = 2
        logger.handlers[1].setLevel(logging.WARNING)
    elif verbose == 3:
        gParamDict["verbose"] = 3
        logger.handlers[1].setLevel(logging.DEBUG)
    else:
        gParamDict["verbose"] = 0

    import os
    for root, subdir, files in os.walk(gParamDict["dir_path"]):
        for _ in files:
            if ".git" in subdir:
                gitx(os.path.abspath(root))
                break
    # Print some tips at last
    if gParamDict["dry_run"]:
        console.print("*" * 80)
        console.print(
            "In order to take effect,run the CLI add option '--dry_run False'")


if __name__ == "__main__":
    from datetime import datetime
    import logging
    import os
    import pathlib
    import sys
    from rich.console import Console
    from rich.theme import Theme

    # Define some variable
    console = Console(width=240, theme=Theme(inherit=False))
    style = "black on white"
    datetimeStr = datetime.now().strftime("%Y%m%d%H%M%S%f")
    appDirPath = os.path.dirname(os.path.realpath(__file__))
    gParamDict = {"appDirPath": appDirPath, "console": (console, style)}
    # Create Logger
    logger = logging.getLogger("giat")
    logger.setLevel(logging.DEBUG)
    # Create File Handler
    # Mode set Write
    logDirPath = os.path.join(appDirPath, "./log")
    pathlib.Path(logDirPath).mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(os.path.join(logDirPath,
                                          "giatlog_" + datetimeStr + ".log"),
                             mode="w")
    fh.setLevel(logging.DEBUG)
    # Create Console Handler
    # TODO: split logger to standalone
    ch = logging.StreamHandler()
    ch.setLevel(logging.FATAL)  # default set FATAL
    # Create logging Formatter
    formatter = logging.Formatter(
        "%(asctime)s-%(name)s-%(levelname)s-%(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # Add Handlers to the Logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    # Check Python Version if < 3.8 exit
    if (sys.version_info.major, sys.version_info.minor) < (3, 8):
        logger.error(
            f"current is {sys.version},Please upgrade to python 3.8 and more.")
        sys.exit()
    # giat action ...
    giat()
