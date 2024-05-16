from io import BytesIO
import sys
import unittest

import pytest

BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
CRLF = '\r\n'


@pytest.fixture(scope="function")
def fields():
    from peppercorn import START, END, MAPPING, SEQUENCE

    return [
        ("name", "project1"),
        ("title", "Cool project"),
        (START, "series:%s" % MAPPING),
        ("name", "date series 1"),
        (START, "dates:%s" % SEQUENCE),
        (START, "date:%s" % SEQUENCE),
        ("day", "10"),
        ("month", "12"),
        ("year", "2008"),
        (END, "date:%s" % SEQUENCE),
        (START, "date:%s" % SEQUENCE),
        ("day", "10"),
        ("month", "12"),
        ("year", "2009"),
        (END, "date:%s" % SEQUENCE),
        (END, "dates:%s" % SEQUENCE),
        (END, "series:%s" % MAPPING),
    ]


@pytest.fixture(scope="function")
def body(fields):
    lines = []
    for (key, value) in fields:
        lines.append('--' + BOUNDARY)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        lines.append('')
        lines.append(value)
    lines.append('--' + BOUNDARY + '--')
    lines.append('')

    return CRLF.join(lines)


@pytest.fixture(scope="function")
def body_bytesio(body):
    return BytesIO(body.encode("utf-8"))


@pytest.fixture(scope="function")
def content_type():  # pragma NO COVER Python >= 3.13
    return 'multipart/form-data; boundary=%s' % BOUNDARY


@pytest.fixture(scope="function")
def wsgi_environ():  # pragma NO COVER Python >= 3.13
    return {
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8080",
        "REQUEST_METHOD":"POST",
        "PATH_INFO": "/",
        "QUERY_STRING":"",
    }

@pytest.fixture(scope="function")
def cgi_environ(wsgi_environ, content_type):  # pragma NO COVER Python >= 3.13
    wsgi_environ["CONTENT_TYPE"] = content_type
    wsgi_environ["REQUEST_METHOD"] = "POST"
    return wsgi_environ


@pytest.fixture(scope="function")
def cgi_headers(content_type, body):  # pragma NO COVER Python >= 3.13
    return {
        "content-length": str(len(body)),
        "content-type": content_type,
    }


@pytest.fixture(scope="function")
def cgi_fieldstorage(
    body_bytesio, cgi_environ, cgi_headers
):  # pragma NO COVER Python >= 3.13
    from cgi import FieldStorage

    return FieldStorage(
        fp=body_bytesio,
        environ=cgi_environ,
        keep_blank_values=1,
        headers=headers,
    )


@pytest.fixture(scope="function")
def multipart_multipartparser(body_bytesio):
    from multipart import MultipartParser

    return MultipartParser(body_bytesio, BOUNDARY)


def _assertFieldsResult(result):
    assert result == {
        "series": {
            "name":"date series 1",
            "dates": [
                ["10", "12", "2008"],
                ["10", "12", "2009"],
            ],
            },
            "name": "project1",
            "title": "Cool project"
    }


def test_bare(fields):
    from peppercorn import parse

    result = parse(fields)

    _assertFieldsResult(result)


@pytest.mark.skipif(
    sys.version_info >= (3, 13),
    reason="PEP 594:  'cgi' removed from stdlib",
)
def test_w_cgi_fieldstorage(cgi_fieldstorage):  # pragma NO COVER
    from peppercorn import parse

    fields = [
        (part.name, part.value) for part in cgi_fieldstorage.list
    ]

    result = parse(fields)

    _assertFieldsResult(result)


def test_w_multipart_multipartparse(multipart_multipartparser):
    from peppercorn import parse

    fields = [
        (part.name, part.value) for part in list(multipart_multipartparser)
    ]

    result = parse(fields)

    _assertFieldsResult(result)


def test_bad_start_marker():
    from peppercorn import START
    from peppercorn import parse
    from peppercorn import UnknownStartMarker

    bad_start_fields = [
        (START, "something:unknown"),
    ]
    
    with pytest.raises(UnknownStartMarker):
        parse(bad_start_fields)


def test_unnamed_start_marker():
    from peppercorn import START, END, MAPPING
    from peppercorn import parse

    unnamed_start_fields = [
        (START, MAPPING),
        ("name", "fred"),
        (END, ""),
    ]

    result = parse(unnamed_start_fields)

    assert result == {"": {"name":"fred"}}


def test_rename():
    from peppercorn import START, END, RENAME, MAPPING
    from peppercorn import parse

    rename_fields = [
        (START, MAPPING),
        (START, "name:" + RENAME),
        ("bleev", "fred"),
        ("blam", "joe"),
        ("bloov", "bob"),
        (END, ""),
        (END, ""),
        ]

    result = parse(rename_fields)

    assert result == {"": {"name":"fred"}}
 

def test_rename_no_subelements():
    from peppercorn import START, END, RENAME, MAPPING
    from peppercorn import parse

    rename_fields = [
        (START, MAPPING),
        (START, "name:" + RENAME),
        (END, ""),
        (END, ""),
        ]

    result = parse(rename_fields)

    assert result == {"": {"name":""}}


def test_ignore():
    from peppercorn import START, END, IGNORE, MAPPING
    from peppercorn import parse

    ignore_fields = [
        (START, MAPPING),
        ("name1", "fred"),
        (START, "whatever:" + IGNORE),
        ("name2", "barney"),
        (END, ""),
        ("name3", "wilma"),
        (END, ""),
    ]

    result = parse(ignore_fields)

    assert result == {"": {"name1":"fred", "name3": "wilma"}}


def test_excessive_end_markers():
    from peppercorn import START, END, MAPPING
    from peppercorn import parse
    from peppercorn import TooManyEndMarkers

    eem_fields = [
        (START, MAPPING),
        ("name1", "fred"),
        (END, ""),
        (END, ""),
    ]

    with pytest.raises(TooManyEndMarkers):
        parse(eem_fields)


def test_insufficient_end_markers():
    from peppercorn import START, END, MAPPING
    from peppercorn import parse
    from peppercorn import NotEnoughEndMarkers

    iem_fields = [
        (START, MAPPING),
        ("name1", "fred"),
    ]

    with pytest.raises(NotEnoughEndMarkers):
        parse(iem_fields)
