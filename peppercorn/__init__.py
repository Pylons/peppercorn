START = '__start__'
END = '__end__'
SEQUENCE = 'sequence'
MAPPING = 'mapping'
RENAME = 'rename'


class ParseError(Exception):
    """
    An exception raised when the input is malformed.
    """


class RenameList(list): pass


_COLLECTION_TYPES = {
    SEQUENCE: list,
    MAPPING: dict,
    RENAME: RenameList,
}


def data_type(marker):
    """Extract the name and the data type from a start marker.

    Return the name and a collection instance.
    """
    if ':' in marker:
        name, typ = [ x.strip() for x in marker.rsplit(':', 1) ]
    else:
        name = ''
        typ = marker.strip()
    try:
        collection = _COLLECTION_TYPES[typ]()
    except KeyError:
        raise ParseError('Unknown stream start marker %s' % marker)
    return name, collection


def parse(fields):
    """ Infer a data structure from the ordered set of fields and
    return it.

    A :exc:`ParseError` is raised if a data structure can't be inferred.
    """
    stack = [{}]

    def add_item(name, value):
        """Add an item to the last collection in the stack"""
        current = stack[-1]
        if isinstance(current, dict):
            current[name] = value
        else:
            current.append(value)

    for op, data in fields:
        if op == START:
            name, collection = data_type(data)
            add_item(name, collection)
            # Make future calls to `add_item` work on this collection:
            stack.append(collection)
        elif op == END:
            if len(stack):
                # Replace all instances of RenameList with their first item.
                collection = stack[-1]
                if isinstance(collection, dict):
                    items = collection.items()
                else:
                    items = enumerate(collection)
                rename_info = []
                for key, value in items:
                    if isinstance(value, RenameList):
                        rename_info.append((key, value[0] if value else ''))
                for key, value in rename_info:
                    collection[key] = value

                if len(stack) > 1:
                    stack.pop()
                else:
                    break
        else:
            add_item(op, data)

    if len(stack) > 1:
        raise ParseError('Unclosed sequence')

    return stack[0]
