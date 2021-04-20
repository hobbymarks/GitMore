import random
import string
from giat import giat


def test_rich_style():
    orgs = pros = "".join(
        random.choice(string.ascii_letters + string.digits +
                      string.punctuation) for idx in range(64))
    rich_orgs, rich_pros = giat.rich_style(orgs, pros)
    assert (rich_orgs == orgs) and (rich_pros == pros)


def test_get_git_config():
    assert giat.get_git_config(None) is None
    assert giat.get_git_config("./tmp") is None


def test_gitx():
    assert False


def test_giat():
    assert False