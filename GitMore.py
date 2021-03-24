#!/usr/bin/env python
import click


def richStyle(originString="", processedString=""):
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
    import os
    import re
    if (gitRepoPath is None) or (not os.path.exists(gitRepoPath)):
        print(f"Not Valid Path:{gitRepoPath}\nPlease Check Again!")
        return None
    if not os.path.isdir(os.path.join(gitRepoPath, ".git")):
        print(f"Not Valid Git Repo Path:{gitRepoPath}\nPlease Check Again!")
        return None
    configPath = os.path.join(gitRepoPath, ".git/config")
    if not os.path.isfile(configPath):
        print(f"No Valid Configuration:{gitRepoPath}\nPlease Check Again!")
        return None
    rePattern = ".*github.com/(.*)/(.*).git.*"
    with open(configPath, "r") as fhandle:
        for line in fhandle:
            reMatch = re.match(rePattern, line)
            if not reMatch is None:
                return reMatch.groups()


def gitX(gitRepoPath=None):
    logDirPath = globalParameterDictionary["logDirPath"]
    console, style = globalParameterDictionary["console"]
    result = getGitConfiguration(gitRepoPath)
    newRepoName = None if result is None else str(result[1]) + "@" + str(
        result[0])
    if newRepoName is None:
        print(f"No Valid Configuration found.")
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
        with open(logPath, "wb") as fhandle:
            pickle.dump(logContent, fhandle)
        os.rename(currentRepoPath, newRepoPath)
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
                gitX(root)
                break


if __name__ == "__main__":
    import os
    import sys
    from rich.console import Console
    from rich.theme import Theme
    console = Console(width=240, theme=Theme(inherit=False))
    style = "black on white"
    if (sys.version_info.major, sys.version_info.minor) < (3, 8):
        console.print(
            f"current Version is {sys.version},\n Please upgrade to at least 3.8."
        )
        sys.exit()
    scriptDirPath = os.path.dirname(os.path.realpath(__file__))

    globalParameterDictionary = {}
    globalParameterDictionary["logDirPath"] = os.path.join(
        scriptDirPath, "data")
    globalParameterDictionary["console"] = (console, style)
    gitMore()
