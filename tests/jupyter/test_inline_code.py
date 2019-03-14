import pytest


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(["begin\npy{{a=1}}e{{a;b}}end"])
    return source_simple


def test_render_inline_code(parser, jupyter, source_simple):
    splitter = parser.splitter(source_simple)
    next(splitter)
    cell = splitter.send(all)
    cell = splitter.send(all)
    assert cell["context"] == {"code": "a=1"}
    cell = splitter.send(all)
    cell = splitter.send(all)
    assert cell["context"] == {"code": "a;b"}
