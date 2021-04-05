#!/usr/bin/env python
import click


def richStyle(originString="", processedString=""):
    global globalParamDict
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
    global globalParamDict
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
    rePatternList = [".*github.com/(.*)/(.*).git.*", ".*github.com/(.*)/(.*)"]
    try:
        with open(configPath, "r") as fhandle:
            for line in fhandle:
                for rePattern in rePatternList:
                    reMatch = re.match(rePattern, line)
                    if not reMatch is None:
                        return reMatch.groups()
        logger.debug(f"read git config successfully:{configPath}")
    except:
        e = sys.exc_info()
        logger.error(e)


def gitX(gitRepoPath=None):
    import logging
    import pathlib
    logger = logging.getLogger("GitMore")
    global globalParamDict
    dataDirPath = globalParamDict["dataDirPath"]
    pathlib.Path(dataDirPath).mkdir(parents=True, exist_ok=True)
    console, style = globalParamDict["console"]
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
    if not globalParamDict["dry"]:
        datetimeStr = datetime.now().strftime("%Y%m%d%H%M%S%f")
        logContent = {
            "current": newRepoPath,
            "history": {
                datetimeStr: currentRepoPath
            }
        }
        dataPath = os.path.join(
            dataDirPath,
            hashlib.md5(newRepoPath.encode("UTF-8")).hexdigest() + "_" +
            datetimeStr + ".pkl")
        try:
            with open(dataPath, "wb") as fhandle:
                pickle.dump(logContent, fhandle)
            logger.debug(f"write {dataPath} successfully.")
        except:
            e = sys.exc_info()
            logger.error(e)
        try:
            os.rename(currentRepoPath, newRepoPath)
            logger.debug(
                f"rename {currentRepoName} to {newRepoName} successfully.")
            if globalParamDict["appDirPath"] != os.path.dirname(
                    os.path.realpath(__file__)):
                globalParamDict["appDirPath"] = os.path.dirname(
                    os.path.realpath(__file__))
                logger.debug(
                    f'Current appDirPath:{globalParamDict["appDirPath"]}')
                globalParamDict["dataDirPath"] = os.path.join(
                    globalParamDict["appDirPath"], "data")
                logger.debug(
                    f'Current dataDirPath:{globalParamDict["dataDirPath"]}')

        except:
            e = sys.exc_info()
            logger.error(e)

    richCurrentRepoPath, richNewRepoPath = richStyle(currentRepoPath,
                                                     newRepoPath)
    console.print(" " * 3 + richCurrentRepoPath, style=style)
    if globalParamDict["dry"]:
        console.print("-->" + richNewRepoPath, style=style)
    else:
        console.print("==>" + richNewRepoPath, style=style)


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("argpath", required=False, type=click.Path(exists=True))
@click.option("--dry",
              default=True,
              type=bool,
              help="If dry is True will not change file name.",
              show_default=True)
def gitMore(argpath, dry):
    global globalParamDict
    """Change Git Local Repo Dir Name to RepoName@OrgName format
    """
    if argpath:
        globalParamDict["argpath"] = argpath
    else:
        globalParamDict["argpath"] = "."
    globalParamDict["dry"] = dry

    import os
    for root, subdir, files in os.walk(globalParamDict["argpath"]):
        for f in files:
            if ".git" in subdir:
                gitX(os.path.abspath(root))
                break
    if globalParamDict["dry"]:
        console.print("*" * 80)
        console.print(
            "In order to take effect,run the CLI add option '--dry False'")


if __name__ == "__main__":
    from datetime import datetime
    import logging
    import os
    import pathlib
    import sys
    from rich.console import Console
    from rich.theme import Theme
    #Define some varible
    console = Console(width=240, theme=Theme(inherit=False))
    style = "black on white"
    datetimeStr = datetime.now().strftime("%Y%m%d%H%M%S%f")
    appDirPath = os.path.dirname(os.path.realpath(__file__))
    globalParamDict = {}
    globalParamDict["appDirPath"] = appDirPath
    globalParamDict["dataDirPath"] = os.path.join(globalParamDict["appDirPath"],
                                                  "data")
    globalParamDict["console"] = (console, style)
    #Create Logger
    logger = logging.getLogger("GitMore")
    logger.setLevel(logging.DEBUG)
    #Create File Handler
    #Mode set Write
    logDirPath = os.path.join(appDirPath, "./log")
    pathlib.Path(logDirPath).mkdir(parents=True, exist_ok=True)
    fhandle = logging.FileHandler(os.path.join(
        logDirPath, "GitMorelog_" + datetimeStr + ".log"),
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
