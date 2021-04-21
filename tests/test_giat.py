import os
import random
import shutil
import string
import uuid
from giat import giat
import pytest


@pytest.fixture
def temporary_path(tmp_path):
    yield tmp_path
    shutil.rmtree(tmp_path)


nonexist_path = str(uuid.uuid1()).replace("-", "")
nonexit_gitpath_data = [(None, None), (nonexist_path, None)]


def test_rich_style():
    orgs = pros = "".join(
        random.choice(string.ascii_letters + string.digits +
                      string.punctuation) for _ in range(64))
    rich_orgs, rich_pros = giat.rich_style(orgs, pros)
    assert (rich_orgs == orgs) and (rich_pros == pros)


@pytest.mark.parametrize("gitpath,result", nonexit_gitpath_data)
def test_get_git_config_nonexist_path(gitpath, result):
    assert giat.get_git_config(gitpath) == result
#
#
# def test_get_git_config_nongit_path(temporary_path):
#     assert giat.get_git_config(temporary_path) is None

#
# def test_get_git_config_nonvalid_gitpath(temporary_path):
#     os.mkdir(os.path.join(temporary_path, ".git"))
#     assert giat.get_git_config(temporary_path) is None
#
#
# def test_get_git_config_nonvalid_config(temporary_path):
#     os.makedirs(os.path.join(temporary_path, ".git/"))
#     with open(os.path.join(os.path.join(temporary_path, ".git/"), "config"),
#               "w") as fh:
#         fh.write("test...firstLine")
#         fh.write("test...secondLine")
#     assert giat.get_git_config(temporary_path) is None
#
#
# def test_get_git_config_valid_config(temporary_path):
#     os.makedirs(os.path.join(temporary_path, ".git/"))
#     with open(os.path.join(os.path.join(temporary_path, ".git/"), "config"),
#               "w") as fh:
#         fh.write("github.com/Org/Repo\n")
#         fh.write("test...secondLine")
#     assert giat.get_git_config(temporary_path) == ("Org", "Repo")


###############################################################################
def test_gitx_none_path():
    assert giat.gitx(None) is None


def test_gitx_nongit_path(temporary_path):
    assert giat.gitx(temporary_path) is None


def test_gitx_config_nonvalid_gitpath(temporary_path):
    os.mkdir(os.path.join(temporary_path, ".git"))
    assert giat.gitx(temporary_path) is None


def test_gitx_nonvalid_config(temporary_path):
    os.makedirs(os.path.join(temporary_path, ".git/"))
    with open(os.path.join(os.path.join(temporary_path, ".git/"), "config"),
              "w") as fh:
        fh.write("test...firstLine")
        fh.write("test...secondLine")
    assert giat.gitx(temporary_path) is None


def test_gitx_valid_config(temporary_path):
    os.makedirs(os.path.join(temporary_path, ".git/"))
    with open(os.path.join(os.path.join(temporary_path, ".git/"), "config"),
              "w") as fh:
        fh.write("github.com/Org/Repo\n")
        fh.write("test...secondLine")
    assert giat.gitx(temporary_path) is None

###############################################################################

def test_giat():
    assert giat.giat("","./",None) is None
