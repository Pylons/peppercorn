
START = '__start__'
END = '__end__'
SEQUENCE = 'sequence'
MAPPING = 'mapping'
RENAME = 'rename'
IGNORE = 'ignore'
TYPS = (SEQUENCE, MAPPING, RENAME, IGNORE)


def data_type(value):
    if ':' in value:
        return [ x.strip() for x in value.rsplit(':', 1) ]
    return ('', value.strip())


class UnknownStartMarker(ValueError):
    def __init__(self, token):
        self.token = token
        super().__init__(
            f"Unknown start marker {repr(token)}"
        )


class TooManyEndMarkers(ValueError):
    def __init__(self):
        super().__init__("Too many end markers")


class NotEnoughEndMarkers(ValueError):
    def __init__(self):
        super().__init__("Not enough end markers")


def parse(tokens, unique_key_separator=None):
    """ Infer a data structure from the ordered set of fields and
    return it."""
    target = typ = None
    out = []    # [(key, value)]
    stack = []  # [(target, typ, out)]

    for token in tokens:
        key, val = token

        if unique_key_separator:
            key = key.rsplit(unique_key_separator, maxsplit=1)[0]

        if key == START:
            stack.append((target, typ, out))
            target, typ = data_type(val)

            if typ in TYPS:
                out = []
            else:
                raise UnknownStartMarker(token)

        elif key == END:

            if typ == SEQUENCE:
                parsed = [v for (k, v) in out]
            elif typ == MAPPING:
                parsed = dict(out)
            elif typ == RENAME:
                parsed = out[0][1] if out else ''
            elif typ == IGNORE:
                parsed = None
            else:
                raise TooManyEndMarkers()

            prev_target, prev_typ, out = stack.pop()
            if parsed is not None:
                out.append((target, parsed))
            target = prev_target
            typ = prev_typ

        else:
            out.append((key, val))

    if stack:
        raise NotEnoughEndMarkers()

    return dict(out)
