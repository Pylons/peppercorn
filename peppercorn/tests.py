from io import BytesIO
import unittest

import pytest

BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
CRLF = '\r\n'

@pytest.fixture(scope="function")
def environ():
    return {
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8080",
        "REQUEST_METHOD":"POST",
        "PATH_INFO": "/",
        "QUERY_STRING":"",
    }


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
def content_type():
    return 'multipart/form-data; boundary=%s' % BOUNDARY


@pytest.fixture(scope="function")
def environ_for_mpfs(environ, content_type):
    environ["CONTENT_TYPE"] = content_type
    environ["REQUEST_METHOD"] = "POST"
    return environ


@pytest.fixture(scope="function")
def headers(content_type, body):
    return {
        "content-length": str(len(body)),
        "content-type": content_type,
    }


@pytest.fixture(scope="function")
def cgi_fieldstorage(body_bytesio, environ_for_mpfs, headers):
    from cgi import FieldStorage

    return FieldStorage(
        fp=body_bytesio,
        environ=environ_for_mpfs,
        keep_blank_values=1,
        headers=headers,
    )


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


def test_w_cgi_fieldstorage(cgi_fieldstorage):
    from peppercorn import parse

    fields = []

    for field in cgi_fieldstorage.list:
        fields.append((field.name, field.value))

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
