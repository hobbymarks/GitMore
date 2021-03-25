#!/usr/bin/env python
import click


def richStyle(originString="", processedString=""):
    global globalParameterDictionary
    import difflib
    richS1 = richS2 = ""
    richS1DifPos = richS2DifPos = 0
    for match in difflib.SequenceMatcher(0, originString,
                                         processedString).get_matching_blocks():
        if richS1DifPos < match.a:
            richS1 += "[bold red]" + originString[richS1DifPos:match.a].replace(
                " ", "▯") + "[/bold red]" + originString[match.a:match.a +
                                                         match.size]
            richS1DifPos = match.a + match.size
        else:
            richS1 += originString[match.a:match.a + match.size]
            richS1DifPos = match.a + match.size

        if richS2DifPos < match.b:
            richS2 += "[bold green]" + processedString[
                richS2DifPos:match.b].replace(
                    " ",
                    "▯") + "[/bold green]" + processedString[match.b:match.b +
                                                             match.size]
            richS2DifPos = match.b + match.size
        else:
            richS2 += processedString[match.b:match.b + match.size]
            richS2DifPos = match.b + match.size

    return richS1, richS2


def getGitConfiguration(gitRepoPath=None):
    import logging
    logger = logging.getLogger("GitMore")
    global globalParameterDictionary
    import os
    import re
    if (gitRepoPath is None) or (not os.path.exists(gitRepoPath)):
        logger.warning(f"Not Valid Path:{gitRepoPath}")
        return None
    if not os.path.isdir(os.path.join(gitRepoPath, ".git")):
        logger.warning(f"Not Valid Git Repo Path:{gitRepoPath}")
        return None
    configPath = os.path.join(gitRepoPath, ".git/config")
    if not os.path.isfile(configPath):
        logger.warning(f"No Valid Configuration:{gitRepoPath}")
        return None
    rePattern = ".*github.com/(.*)/(.*).git.*"
    try:
        with open(configPath, "r") as fhandle:
            for line in fhandle:
                reMatch = re.match(rePattern, line)
                if not reMatch is None:
                    return reMatch.groups()
        logger.debug(f"read git config successfully:{configPath}")
    except:
        e = sys.exc_info()
        logger.error(e)


def gitX(gitRepoPath=None):
    import logging
    logger = logging.getLogger("GitMore")
    global globalParameterDictionary
    logDirPath = globalParameterDictionary["logDirPath"]
    console, style = globalParameterDictionary["console"]
    result = getGitConfiguration(gitRepoPath)
    newRepoName = None if result is None else str(result[1]) + "@" + str(
        result[0])
    if newRepoName is None:
        logger.error(f"No Valid Configuration:{gitRepoPath}")
        return None
    from datetime import datetime
    import hashlib
    import os
    import pickle
    currentRepoName = gitRepoPath.rstrip(os.path.sep).split(os.path.sep)[-1]
    currentRepoDirPath = (os.path.sep).join(
        gitRepoPath.rstrip(os.path.sep).split(os.path.sep)[:-1])
    currentRepoPath = os.path.join(currentRepoDirPath, currentRepoName)
    newRepoPath = os.path.join(currentRepoDirPath, newRepoName)
    if currentRepoPath == newRepoPath:
        logger.debug(f"No Need GitMore:{currentRepoPath}")
        return None
    if not globalParameterDictionary["dry"]:
        datetimeStr = datetime.now().strftime("%Y%m%d%H%M%S%f")
        logContent = {
            "current": newRepoPath,
            "history": {
                datetimeStr: currentRepoPath
            }
        }
        logPath = os.path.join(
            logDirPath,
            hashlib.md5(newRepoPath.encode("UTF-8")).hexdigest() + "_" +
            datetimeStr + ".pkl")
        try:
            with open(logPath, "wb") as fhandle:
                pickle.dump(logContent, fhandle)
            logger.debug(f"write {logPath} successfully.")
        except:
            e = sys.exc_info()
            logger.error(e)
        try:
            os.rename(currentRepoPath, newRepoPath)
            logger.debug(
                f"rename {currentRepoName} to {newRepoName} successfully.")
        except:
            e = sys.exc_info()
            logger.error(e)

    richCurrentRepoPath, richNewRepoPath = richStyle(currentRepoPath,
                                                     newRepoPath)
    console.print(" " * 3 + richCurrentRepoPath, style=style)
    console.print("==>" + richNewRepoPath, style=style)


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("argpath", required=False, type=click.Path(exists=True))
@click.option("--dry",
              default=True,
              type=bool,
              help="If dry is True will not change file name.",
              show_default=True)
def gitMore(argpath, dry):
    global globalParameterDictionary
    """Change Git Local Repo Dir Name to RepoName@OrgName
    """
    if argpath:
        globalParameterDictionary["argpath"] = argpath
    else:
        globalParameterDictionary["argpath"] = "."
    globalParameterDictionary["dry"] = dry

    import os
    for root, subdir, files in os.walk(globalParameterDictionary["argpath"]):
        for f in files:
            if ".git" in subdir:
                gitX(os.path.abspath(root))
                break


if __name__ == "__main__":
    from datetime import datetime
    import logging
    import os
    import sys
    from rich.console import Console
    from rich.theme import Theme
    #Define some varible
    console = Console(width=240, theme=Theme(inherit=False))
    style = "black on white"
    datetimeStr = datetime.now().strftime("%Y%m%d%H%M%S%f")
    scriptDirPath = os.path.dirname(os.path.realpath(__file__))
    globalParameterDictionary = {}
    globalParameterDictionary["logDirPath"] = os.path.join(
        scriptDirPath, "data")
    globalParameterDictionary["console"] = (console, style)
    #Create Logger
    logger = logging.getLogger("GitMore")
    logger.setLevel(logging.DEBUG)
    #Create File Handler
    #Mode set Write
    fhandle = logging.FileHandler(os.path.join(
        scriptDirPath, "./log", "GitMorelog_" + datetimeStr + ".log"),
                                  mode="w")
    fhandle.setLevel(logging.DEBUG)
    #Create Console Handler
    chandle = logging.StreamHandler()
    chandle.setLevel(logging.ERROR)
    #Create Formatter
    formatter = logging.Formatter(
        "%(asctime)s-%(name)s-%(levelname)s-%(message)s")
    fhandle.setFormatter(formatter)
    chandle.setFormatter(formatter)
    #Add Handlers to the Logger
    logger.addHandler(fhandle)
    logger.addHandler(chandle)
    #Check Python Version if < 3.8 exit
    if (sys.version_info.major, sys.version_info.minor) < (3, 8):
        logger.error(
            f"current is {sys.version},Please upgrade to python 3.8 and more.")
        sys.exit()
    #gitMore action ...
    gitMore()
