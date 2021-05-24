import difflib
import hashlib
import os
from pathlib import Path
from typing import Tuple, List, Optional, Generator, Union

# From Third Party
import click
from colorama import Fore
from wcwidth import wcswidth


def is_hidden(f_path: Path) -> bool:
    """
    Check file is hidden or not
    :param f_path: string,file path
    :return: True if is hidden file,False if is not hidden file
    """
    if os.name == "nt":
        import win32api
        import win32con
    if os.name == "nt":
        attribute = win32api.GetFileAttributes(f_path)
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN
                            | win32con.FILE_ATTRIBUTE_SYSTEM)
    else:
        return os.path.basename(f_path).startswith(".")  # linux, osx


def depth_walk(
    top_path: Path,
    top_down: bool = False,
    follow_links: bool = False,
    max_depth: int = 1
) -> Optional[Generator[Tuple[str], List[str], List[str]]]:
    if str(max_depth).isnumeric():
        max_depth = int(max_depth)
    else:
        max_depth = 1
    try:
        names = os.listdir(top_path)
    except FileNotFoundError:
        click.echo(f"Warning:{top_path} not found.")
        return None
    except PermissionError:
        click.echo(f"Warning:{top_path} no permissions.")
        return None
    dirs, non_dirs = [], []
    for name in names:
        if os.path.isdir(os.path.join(top_path, name)):
            dirs.append(name)
        else:
            non_dirs.append(name)
    if top_down:
        yield top_path, dirs, non_dirs
    if max_depth > 1:
        for name in dirs:
            new_path = Path(os.path.join(top_path, name))
            if follow_links or not os.path.islink(new_path):
                for x in depth_walk(new_path, top_down, follow_links,
                                    1 if max_depth == 1 else max_depth - 1):
                    yield x
    if not top_down:
        yield top_path, dirs, non_dirs


def rich_style(
    original: str,
    processed: str,
    pretty: bool = False,
    enhanced_display: bool = False
) -> Union[Tuple[None, None], Tuple[str, str]]:
    if (type(original) is not str) or (type(processed) is not str):
        return None, None

    def _f_d(s: str = "", f_d=None):
        return f_d + s + Fore.RESET

    def _c_f(s: str = "") -> str:
        if pretty:
            return s
        else:
            return ""

    a = original
    b = processed
    a_list = []
    b_list = []
    c_f = ' '
    e = enhanced_display
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a,
                                                       b).get_opcodes():
        if tag == "delete":
            a_list.append(_f_d(a[i1:i2].replace(" ", "▯"), Fore.RED))
            b_list.append(_c_f(c_f * wcswidth(a[i1:i2])))
        elif tag == "equal":
            a_list.append(_f_d(a[i1:i2], Fore.BLACK) if e else a[i1:i2])
            b_list.append(_f_d(b[j1:j2], Fore.BLACK) if e else b[j1:j2])
        elif tag == "replace":
            a_w = wcswidth(a[i1:i2])
            b_w = wcswidth(b[j1:j2])
            if a_w > b_w:
                a_list.append(_f_d(a[i1:i2].replace(" ", "▯"), Fore.RED))
                b_list.append(
                    _c_f(c_f * (a_w - b_w)) +
                    _f_d(b[j1:j2].replace(" ", "▯"), Fore.GREEN))

            elif a_w < b_w:
                a_list.append(
                    _c_f(c_f * (b_w - a_w)) +
                    _f_d(a[i1:i2].replace(" ", "▯"), Fore.RED))

                b_list.append(_f_d(b[j1:j2].replace(" ", "▯"), Fore.GREEN))
            else:
                a_list.append(_f_d(a[i1:i2].replace(" ", "▯"), Fore.RED))
                b_list.append(_f_d(b[j1:j2].replace(" ", "▯"), Fore.GREEN))
        elif tag == "insert":
            a_list.append(_c_f(c_f * wcswidth(b[j1:j2])))
            b_list.append(_f_d(b[j1:j2].replace(" ", "▯"), Fore.GREEN))
    return "".join(a_list), "".join(b_list)


def unify_confirm(x: str = "") -> str:
    return {
        "y": "yes",
        "yes": "yes",
        "n": "no",
        "no": "no",
        "A": "all",
        "all": "all",
        "q": "quit",
        "quit": "quit"
    }.get(x, "no")


###############################################################################


def sha2_id(s: str) -> str:
    return hashlib.sha256(s.encode("UTF-8")).hexdigest()
