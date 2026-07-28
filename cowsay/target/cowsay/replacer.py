import re


def extract_the_cow(cow):
    cow = cow.replace("\r\n", "\n").replace("\r", "\n")
    cow = cow.replace("\u2028", "\n").replace("\u2029", "\n")
    cow = cow.lstrip("\ufeff")
    match = re.search(r'\$the_cow\s*=\s*<<"?\s*EOC\s*"?;*\n([\s\S]+?)\nEOC\n', cow)
    if not match:
        return cow
    result = match.group(1)
    result = result.replace("\\\\", "\\")
    result = result.replace("\\@", "@")
    result = result.replace("\\$", "$")
    return result


def render(cow, variables):
    eyes = variables.get("eyes", "oo")
    eye_l = eyes[0] if len(eyes) > 0 else ""
    eye_r = eyes[1] if len(eyes) > 1 else ""
    tongue = variables.get("tongue", "  ")

    if "$the_cow" in cow:
        cow = extract_the_cow(cow)

    cow = cow.replace("$thoughts", variables.get("thoughts", "\\"))
    cow = cow.replace("$eyes", eyes)
    cow = cow.replace("$tongue", tongue)
    cow = cow.replace("${eyes}", eyes)
    cow = cow.replace("$eye", eye_l, 1)
    cow = cow.replace("$eye", eye_r, 1)
    cow = cow.replace("${tongue}", tongue)

    return cow
