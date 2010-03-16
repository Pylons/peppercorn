def data_type(value):
    if ':' in value:
        return [ x.strip().lower() for x in value.split(':', 1) ]
    return ('', value.strip())

def stream(next, token):
    """
    thanks to the effbot for
    http://effbot.org/zone/simple-iterator-parser.htm
    """
    op, value = token
    if op == '__start__':
        structname, typ = data_type(value)
        if typ.startswith('seq'):
            out = []
            token = next()
            op, value = token
            while op != '__end__':
                name, val = stream(next, token)
                out.append(val)
                token = next()
                op, value = token
            return structname, out
        elif typ.startswith('map'):
            out = {}
            token = next()
            op, value = token
            while op != '__end__':
                name, val = stream(next, token)
                out[name] = val
                token = next()
                op, value = token
            return structname, out
        else:
            raise ValueError('Unknown stream start marker %s' % repr(token))
    else:
        return op, value

def parse(fields):
    """ Infer a data structure from the ordered set of fields and
    return it."""
    fields = [('__start__','main:map')] + list(fields) + [('__end__','')]
    src = iter(fields)
    result = stream(src.next, src.next())[1]
    return result
