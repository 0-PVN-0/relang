import os
import random

from . import replacer

_cows_path = None
_text_cache = {}


def _get_cows_path():
    global _cows_path
    if _cows_path is not None:
        return _cows_path
    path = os.path.join(os.path.dirname(__file__), "..", "cows")
    _cows_path = os.path.normpath(path)
    return _cows_path


def _cow_names_from_files(files):
    return [os.path.splitext(os.path.basename(f))[0] for f in files]


def get(cow):
    if cow not in _text_cache:
        if "\\" in cow or "/" in cow:
            file_path = cow
        else:
            file_path = os.path.join(_get_cows_path(), cow + ".cow")

        with open(file_path, "r", encoding="utf-8") as f:
            _text_cache[cow] = f.read()

    text = _text_cache[cow]

    def render_cow(options):
        return replacer.render(text, options)

    return render_cow


def list():
    files = os.listdir(_get_cows_path())
    return _cow_names_from_files(files)


def list_sync():
    return list()
