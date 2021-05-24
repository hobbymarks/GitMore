import os
import random
import shutil
import string
import uuid
from giat import giatcli
import pytest


@pytest.fixture
def temporary_path(tmp_path):
    yield tmp_path
    shutil.rmtree(tmp_path)


non_exist_path = str(uuid.uuid1()).replace("-", "")
non_exist_git_path_data = [(None, None), (non_exist_path, None)]


def test_rich_style():
    org_str = pro_str = "".join(
        random.choice(string.ascii_letters + string.digits +
                      string.punctuation) for _ in range(64))
    rich_org_str, rich_pro_str = giatcli.rich_style(org_str, pro_str)
    assert (rich_org_str == org_str) and (rich_pro_str == pro_str)


@pytest.mark.parametrize("git_path ,result", non_exist_git_path_data)
def test_get_git_config_non_exist_path(git_path, result):
    assert giatcli.get_git_config(git_path) == result


###############################################################################
def test_gitx_none_path():
    assert giatcli.gitx(None) is None


def test_gitx_not_git_path(temporary_path):
    assert giatcli.gitx(temporary_path) is None


def test_gitx_config_invalid_git_path(temporary_path):
    os.mkdir(os.path.join(temporary_path, ".git"))
    assert giatcli.gitx(temporary_path) is None


def test_gitx_invalid_config(temporary_path):
    os.makedirs(os.path.join(temporary_path, ".git/"))
    with open(os.path.join(os.path.join(temporary_path, ".git/"), "config"),
              "w") as fh:
        fh.write("test...firstLine")
        fh.write("test...secondLine")
    assert giatcli.gitx(temporary_path) is None


def test_gitx_valid_config(temporary_path):
    os.makedirs(os.path.join(temporary_path, ".git/"))
    with open(os.path.join(os.path.join(temporary_path, ".git/"), "config"),
              "w") as fh:
        fh.write("github.com/Org/Repo\n")
        fh.write("test...secondLine")
    assert giatcli.gitx(temporary_path) is None


###############################################################################


def test_giat():
    assert giatcli.giat("", "./", None) is None
