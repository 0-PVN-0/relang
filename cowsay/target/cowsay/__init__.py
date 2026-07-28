import random

from . import balloon
from . import cows
from . import faces


def say(options):
    return _do_it(options, True)


def think(options):
    return _do_it(options, False)


def list(callback=None):
    result = cows.list()
    if callback:
        callback(None, result)
    return result


def _do_it(options, say_aloud):
    if options.get("r"):
        cows_list = cows.list_sync()
        cow_file = random.choice(cows_list)
    else:
        cow_file = options.get("f", "default")

    cow_fn = cows.get(cow_file)
    face = faces.get_face(options)
    face["thoughts"] = "\\" if say_aloud else "o"

    action = "say" if say_aloud else "think"
    text = options.get("text") or " ".join(options.get("_", []))
    wrap = None if options.get("n") else options.get("W", 40)
    return balloon.__dict__[action](text, wrap) + "\n" + cow_fn(face)
