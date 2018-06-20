"""Provides the WXXMLParser class."""

import wx
from wx.lib.agw.floatspin import FloatSpin
from wx.lib.intctrl import IntCtrl
from .base import XMLParser


class DuplicateSizerError(Exception):
    """There is already a main sizer."""


class NoParent:
    """Used to specify a default panel should not be created."""

    def __str__(self):
        return 'No Parent'

    def __repr__(self):
        return str(self)


no_parent = NoParent()


class WXXMLParser(XMLParser):
    """Populate wx.Frame instances from XML."""

    def populate_from_root(self, root, frame, parent=no_parent):
        """
        Overrides the default populate_from_root to add wx-specific code. In
        particular the parent argument.

        If parent is no_parent, then parent will be frame.
        If parent is None, then a wx.Panel will be created with frame as its
        only argument.

        Any controls created will have parent as their first argument. As such,
        parent should end up as either frame, or a wx.Panel instance created
        with frame as the parent (parent=None).

        Each parse_* method should be prepared to take 4 arguments:
        node: The node to parse.
        frame: The frame to add controls to (when they have an attribute called
        name).
        parent: The parent to use for control creation.
        sizer: The sizer the created control should be added to.

        Everything else is the same.
        """
        sizer = None
        if parent is no_parent:
            parent = frame
        elif parent is None:
            parent = wx.Panel(frame)
        for node in root:
            res = self.parse_node(node, frame, parent, sizer)
            if isinstance(res, wx.Sizer):
                if sizer is not None:
                    raise DuplicateSizerError(
                        'Sizer %r is the second sizer (first was %r).' % (
                            res, sizer
                        )
                    )
                sizer = res
        if sizer is not None:
            parent.SetSizerAndFit(res)

    def get_flags(self, text, default=0):
        """Given a string like "te_rich2,te_password", return
        wx.TE_RICH2 | wx.TE_PASSWORD."""
        for entry in text.upper().split(','):
            entry = entry.strip()
            default |= getattr(wx, entry)
        return default

    def parse_node(self, node, frame, parent, sizer):
        """Parse a single node."""
        res = super().parse_node(node, frame, parent, sizer)
        a = node.attrib
        label = a.get('label', None)
        if label is not None:
            res.SetLabel(label)
        style = a.get('style', None)
        if style is not None:
            res.SetWindowStyle(self.get_flags(style))
        size = a.get('size', None)
        if size is not None:
            size = self.get_list(size)
            res.SetSize(size)
        if sizer is not None:
            proportion = int(a.get('sizer_proportion', '0'))
            flags = a.get('sizer_flag', 'grow')
            flags = self.get_flags(flags)
            sizer.Add(res, proportion, flags)
        binders = a.get('bind', None)
        if binders is not None:
            for binder in binders.split(','):
                event_name, func_name = binder.split(':')
                event = getattr(wx, f'EVT_{event_name.upper()}')
                func = getattr(self, func_name)
                res.Bind(event, func)
        return res

    def parse_title(self, node, frame, parent, sizer):
        """Add a title to frame."""
        frame.SetTitle(node.text)

    def parse_sizer(self, node, frame, parent, sizer):
        """Parse a sizer and all contained nodes."""
        flags = self.get_flags(node.attrib.get('orient', 'horizontal'))
        s = wx.BoxSizer(flags)
        for child in node:
            self.parse_node(child, frame, parent, s)
        return s

    def parse_label(self, node, frame, parent, sizer):
        """Create a label."""
        return wx.StaticText(parent, label=node.text)

    def parse_text(self, node, frame, parent, sizer):
        """Create a text control."""
        return wx.TextCtrl(parent, value=node.text or '')

    def parse_integer(self, node, frame, parent, sizer):
        """Create a control that accepts integers."""
        a = node.attrib
        min_value = a.get('min', None)
        if min_value is not None:
            min_value = int(min_value)
        max_value = a.get('max', None)
        if max_value is not None:
            max_value = int(max_value)
        limited = int(a.get('limited', 0))
        allow_none = int(a.get('allow_none', 0))
        allow_long = int(a.get('allow_long', 0))
        value = node.text
        if value is None:
            value = 0
        else:
            value = int(value)
        return IntCtrl(
            parent, min=min_value, max=max_value, limited=limited,
            allow_none=allow_none, allow_long=allow_long, value=value
        )

    def parse_float(self, node, frame, parent, sizer):
        """Return a float control."""
        if node.text is None:
            value = 0.0
        else:
            value = float(node.text)
        a = node.attrib
        min_value = a.get('min', None)
        if min_value is not None:
            min_value = float(min_value)
        max_value = a.get('max', None)
        if max_value is not None:
            max_value = float(max_value)
        increment = float(a.get('increment', 1.0))
        digits = int(a.get('digits', -1))
        return FloatSpin(
            parent, value=value, min_val=min_value, max_val=max_value,
            increment=increment, digits=digits
        )

    def parse_slider(self, node, frame, parent, sizer):
        """Return a slider control."""
        if node.text is None:
            value = 0
        else:
            value = int(node.text)
        a = node.attrib
        min_value = int(a.get('min', 0))
        max_value = int(a.get('max', 100))
        return wx.Slider(
            parent, value=value, minValue=min_value, maxValue=max_value
        )

    def parse_checkbox(self, node, frame, parent, sizer):
        """Return a checkbox."""
        cb = wx.CheckBox(parent)
        if node.text is not None:
            cb.SetValue(int(node.text))
        return cb

    def parse_button(self, node, frame, parent, sizer):
        """Returns a button."""
        a = node.attrib
        b = wx.Button(parent)
        default = int(a.get('default', 0))
        if default:
            b.SetDefault()
        return b
