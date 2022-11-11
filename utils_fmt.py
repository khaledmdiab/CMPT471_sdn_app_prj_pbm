def none_to_star(s):
    return "*" if s is None else s

def format_without_nones(format_string, *args):
    return format_string.format(*map(none_to_star, args))