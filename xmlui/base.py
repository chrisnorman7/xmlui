"""XMLUI: Build user interfaces from XML files.
By default uses wxpython."""

from xml.etree.ElementTree import fromstring, parse
from .exc import NoParserError


class XMLParser:
    """Add controls coded as XML to a frame."""

    def populate_from_string(self, string, *args, **kwargs):
        """Populate a frame from a string containing XML."""
        root = fromstring(string)
        return self.populate_from_root(root, *args, **kwargs)

    def populate_from_file(self, f, *args, **kwargs):
        """Uses ElementTree.parse to load xml before calling
        populate_from_root."""
        tree = parse(f)
        root = tree.getroot()
        return self.populate_from_root(root, *args, **kwargs)

    def populate_from_root(self, root, frame, *args, **kwargs):
        """Given an XML tree starting at root, parses all tags using methods
        defined on this class as parse_tag - where tag is the name of a tag to
        parse - and populates the given frame with them.

        A special method parse_node is used to parse nodes.

        If necessary, a parse_* method should be prepared to recurse through
        any subnodes as appropriate."""
        for node in root:
            self.parse_node(node, frame, *args, **kwargs)

    def get_list(self, text, start=None, function=int):
        """Takes text line "5, 4" and returns [5, 4]."""
        if start is None:
            start = []
        for entry in text.split(','):
            start.append(function(entry.strip()))
        return start

    def parse_node(self, node, frame, *args, **kwargs):
        """Parses a single node."""
        func = getattr(self, f'parse_{node.tag}', None)
        if func is None:
            raise NoParserError(node.tag)
        res = func(node, frame, *args, **kwargs)
        a = node.attrib
        name = a.get('name', None)
        if name is not None:
            setattr(frame, name, res)
        return res
