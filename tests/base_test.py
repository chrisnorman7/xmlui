"""Test the base XMLParser class."""

from pytest import raises
from xmlui.base import XMLParser
from xmlui.exc import NoParserError

works_code = """
<frame>
    <works></works>
</frame>
"""

fails_code = """
<frame>
    <fails></fails>
</frame>
"""

name_code = """
<frame>
    <tag name="pretend"></tag>
</frame>
"""


class NodeWorks(Exception):
    pass


class Tag:
    """A pretend tag."""


tag = Tag()


class DummyFrame:
    """A pretend frame class."""


class MyXMLParser(XMLParser):

    def parse_works(self, node, frame):
        raise NodeWorks()

    def parse_tag(self, node, frame):
        """Simply return tag."""
        return tag


xml = MyXMLParser()


def test_works():
    with raises(NodeWorks):
        xml.populate_from_string(works_code, None)


def test_fails():
    with raises(NoParserError) as exc:
        xml.populate_from_string(fails_code, None)
    assert exc.value.args == ('fails',)


def test_name():
    frame = DummyFrame()
    xml.populate_from_string(name_code, frame)
    assert frame.pretend is tag


def test_get_list_default():
    assert xml.get_list('1, 2, 3') == [1, 2, 3]


def test_get_list_with_start():
    assert xml.get_list('2, 3, 4', start=[1]) == [1, 2, 3, 4]


def test_get_list_with_func():
    assert xml.get_list('1,2,3,4', function=float) == [1.0, 2.0, 3.0, 4.0]
