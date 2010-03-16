def data_type(value):
    if ':' in value:
        return [ x.strip() for x in value.rsplit(':', 1) ]
    return ('', value.strip())

START = '__start__'
END = '__end__'
SEQUENCE = 'sequence'
MAPPING = 'mapping'

def stream(next, token):
    """
    thanks to the effbot for
    http://effbot.org/zone/simple-iterator-parser.htm
    """
    op, data = token
    if op == START:
        name, typ = data_type(data)
        if typ in (SEQUENCE, MAPPING):
            if typ == SEQUENCE:
                out = []
                add = lambda x, y: out.append(y)
            else:
                out = {}
                add = out.__setitem__
            token = next()
            op, data = token
            while op != END:
                key, val = stream(next, token)
                add(key, val)
                token = next()
                op, data = token
            return name, out
        else:
            raise ValueError('Unknown stream start marker %s' % repr(token))
    else:
        return op, data

def parse(fields):
    """ Infer a data structure from the ordered set of fields and
    return it."""
    fields = [(START, MAPPING)] + list(fields) + [(END,'')]
    src = iter(fields)
    result = stream(src.next, src.next())[1]
    return result
