MODES = {
    "b": {"eyes": "==", "tongue": "  "},
    "d": {"eyes": "xx", "tongue": "U "},
    "g": {"eyes": "$$", "tongue": "  "},
    "p": {"eyes": "@@", "tongue": "  "},
    "s": {"eyes": "**", "tongue": "U "},
    "t": {"eyes": "--", "tongue": "  "},
    "w": {"eyes": "OO", "tongue": "  "},
    "y": {"eyes": "..", "tongue": "  "},
}


def get_face(options):
    for mode, face in MODES.items():
        if options.get(mode):
            return dict(face)
    return {
        "eyes": options.get("e", "oo"),
        "tongue": options.get("T", "  "),
    }
