"""Test the wx stuff."""

from pytest import raises
from xml.etree.ElementTree import Element
import wx
from wx.lib.intctrl import IntCtrl
from wx.lib.agw.floatspin import FloatSpin
from xmlui.wx import (
    WXXMLParser, DuplicateSizerError, NoParent, no_parent, NoValueError,
    InvalidTagError
)

app = wx.App()  # Keep wx happy.

xml = WXXMLParser()
root = Element('frame')

duplicate_sizers_code = """
<frame>
    <sizer></sizer>
    <sizer></sizer>
</frame>
"""


def test_no_parent():
    assert isinstance(no_parent, NoParent)


def test_no_panel():
    f = wx.Frame(None)
    xml.populate_from_root(root, f)
    assert not f.GetChildren()
    f.Destroy()


def test_create_panel():
    f = wx.Frame(None)
    xml.populate_from_root(root, f, parent=None)
    assert len(f.GetChildren()) == 1
    assert isinstance(f.GetChildren()[0], wx.Panel)
    f.Destroy()


def test_provide_panel():
    f = wx.Frame(None)
    p = wx.Panel(f)
    xml.populate_from_root(root, f, p)
    assert len(f.GetChildren()) == 1
    assert f.GetChildren()[0] is p


def test_multiple_sizers():
    f = wx.Frame(None)
    with raises(DuplicateSizerError):
        xml.populate_from_string(duplicate_sizers_code, f)
    f.Destroy()


def test_flags_no_default():
    assert xml.get_flags('te_rich,te_password') == wx.TE_RICH | wx.TE_PASSWORD


def test_flags_with_default():
    assert xml.get_flags('te_rich2, te_password', default=wx.TE_RICH) == (
        wx.TE_RICH | wx.TE_RICH2 | wx.TE_PASSWORD
    )


def test_sizer():
    root = Element('sizer', orient='vertical')
    f = wx.Frame(None)
    s = xml.parse_sizer(root, f, None, None)
    assert isinstance(s, wx.BoxSizer)
    assert s.GetOrientation() == wx.VERTICAL
    f.Destroy()


def test_title():
    root = Element('title')
    root.text = 'Test Title'
    f = wx.Frame(None)
    res = xml.parse_title(root, f, None, None)
    assert res is None
    assert f.GetTitle() == root.text
    f.Destroy()


def test_label():
    root = Element('label')
    root.text = 'Test Label'
    f = wx.Frame(None)
    label = xml.parse_label(root, f, f, None)
    assert isinstance(label, wx.StaticText)
    assert label.GetLabel() == root.text
    f.Destroy()


def test_text_blank():
    root = Element('text')
    f = wx.Frame(None)
    t = xml.parse_text(root, f, f, None)
    assert isinstance(t, wx.TextCtrl)
    assert t.GetValue() == ''
    f.Destroy()


def test_text_filled():
    root = Element('text')
    root.text = 'Testing'
    f = wx.Frame(None)
    t = xml.parse_text(root, f, f, None)
    assert t.GetValue() == root.text
    f.Destroy()


def test_integer():
    root = Element(
        'integer', min='4', max='400', limited='1', allow_none='1',
        allow_long='1'
    )
    root.text = '55'
    f = wx.Frame(None)
    i = xml.parse_integer(root, f, f, None)
    assert isinstance(i, IntCtrl)
    assert i.GetMin() == 4
    assert i.GetMax() == 400
    assert i.IsLimited() == 1
    assert i.IsNoneAllowed() == 1
    assert i.IsLongAllowed() == 1
    assert i.GetValue() == 55
    f.Destroy()


def test_float():
    root = Element(
        'float', min='0.5', max='100.5', increment='1.0', digits='2'
    )
    root.text = '12.3'
    frame = wx.Frame(None)
    f = xml.parse_float(root, frame, frame, None)
    assert isinstance(f, FloatSpin)
    assert f.GetValue() == 12.3
    assert f.GetMin() == 0.5
    assert f.GetMax() == 100.5
    assert f.GetDigits() == 2
    assert f.GetIncrement() == 1.0
    frame.Destroy()


def test_slider():
    root = Element('slider', min='10', max='50')
    root.text = '15'
    f = wx.Frame(None)
    s = xml.parse_slider(root, f, f, None)
    assert isinstance(s, wx.Slider)
    assert s.GetValue() == 15
    assert s.GetMin() == 10
    assert s.GetMax() == 50
    f.Destroy()


def test_checkbox_unchecked():
    root = Element('checkbox')
    f = wx.Frame(None)
    cb = xml.parse_checkbox(root, f, f, None)
    assert isinstance(cb, wx.CheckBox)
    assert not cb.GetValue()
    f.Destroy()


def test_checkbox_checked():
    root = Element('checkbox')
    root.text = '1'
    f = wx.Frame(None)
    assert xml.parse_checkbox(root, f, f, None).GetValue()
    f.Destroy()


def test_button_not_default():
    root = Element('Button')
    f = wx.Frame(None)
    assert isinstance(xml.parse_button(root, f, f, None), wx.Button)
    assert f.GetDefaultItem() is None
    f.Destroy()


def test_button_default():
    root = Element('button', default='1')
    f = wx.Frame(None)
    b = xml.parse_button(root, f, f, None)
    assert isinstance(b, wx.Button)
    assert f.GetDefaultItem() is b
    f.Destroy()


def test_parse_node():
    root = Element(
        'button', label='&Test', style='bu_exactfit', size='45, 55',
        sizer_proportion='2', sizer_flag='all'
    )
    s = wx.BoxSizer()
    f = wx.Frame(None)
    b = xml.parse_node(root, f, f, s)
    assert b.GetLabel() == '&Test'
    assert b.GetWindowStyle() == wx.BU_EXACTFIT
    assert b.GetSize() == (45, 55)
    assert len(s.GetChildren()) == 1
    i = s.GetChildren()[0]
    assert i.Window is b
    assert i.GetProportion() == 2
    assert i.GetFlag() == wx.ALL
    f.Destroy()


def test_choice():
    choices = ['First', 'Second', 'Third']
    root = Element('choice', choices=', '.join(choices))
    root.text = '1'
    f = wx.Frame(None)
    c = xml.parse_node(root, f, f, None)
    assert c.GetStrings() == choices
    assert c.GetStringSelection() == choices[1]
    f.Destroy()


def test_list():
    root = Element('list', choices='First, Second, Third')
    root.text = '1'
    f = wx.Frame(None)
    c = xml.parse_node(root, f, f, None)
    assert isinstance(c, wx.ListBox)
    assert c.GetStrings() == ['First', 'Second', 'Third']
    assert c.GetStringSelection() == 'Second'
    f.Destroy()


def test_column():
    root = Element('column')
    args = (root, None, None, None)
    with raises(NoValueError):
        xml.parse_column(*args)
    root.text = 'Test'
    heading, format, width = xml.parse_column(*args)
    assert heading == root.text
    assert format == wx.LIST_FORMAT_LEFT
    assert width == -1
    root.attrib['width'] = '1234'
    heading, format, width = xml.parse_column(*args)
    assert width == 1234
    root.attrib['format'] = 'list_format_right'
    heading, format, width = xml.parse_column(*args)
    assert format == wx.LIST_FORMAT_RIGHT


def test_item():
    root = Element('item')
    root.text = 'First, Second, Third'
    i = xml.parse_item(root, None, None, None)
    assert i == ['First', 'Second', 'Third']


def test_invalid_tag():
    root = Element('table')
    fail = Element('fails')
    root.append(fail)
    f = wx.Frame(None)
    with raises(InvalidTagError) as exc:
        xml.parse_node(root, f, f, None)
    assert exc.value.args == (fail,)
    f.Destroy()


def test_table_empty():
    root = Element('table')
    col1 = Element('column')
    col1.text = 'First Column'
    col2 = Element('column')
    col2.text = 'Second Column'
    col3 = Element('column')
    col3.text = 'Third Column'
    root.extend([col1, col2, col3])
    assert col1.text is not None
    assert col2.text is not None
    assert col3.text is not None
    assert len(root) == 3
    f = wx.Frame(None)
    c = xml.parse_node(root, f, f, None)
    assert isinstance(c, wx.ListCtrl)
    assert c.GetColumnCount() == 3
    for x, node in enumerate((col1, col2, col3)):
        li = c.GetColumn(x)
        assert li.Text == node.text
    f.Destroy()


def test_table_items_no_columns():
    root = Element('table')
    item = Element('item')
    item.text = 'Testing stuff'
    root.append(item)
    f = wx.Frame(None)
    c = xml.parse_node(root, f, f, None)
    assert c.GetColumnCount() == 0
    assert c.GetItemCount() == 1
    assert c.GetItem(0).Text == item.text


def test_table_with_columns():
    # Only wx.ListCtrl instances wiuth a style of wx.LC_REPORT can contain
    # columns.
    root = Element('table', style='lc_report')
    col1 = Element('column')
    col1.text = 'First Column'
    col2 = Element('column')
    col2.text = 'Second Column'
    col3 = Element('column')
    col3.text = 'Third Column'
    root.extend([col1, col2, col3])
    assert col1.text is not None
    assert col2.text is not None
    assert col3.text is not None
    assert len(root) == 3
    item1 = Element('item')
    item1.text = '1, 2, 3'
    item2 = Element('item')
    item2.text = '4, 5, 6'
    assert item1.text is not None
    assert item2.text is not None
    root.extend([item1, item2])
    assert len(root) == 5
    f = wx.Frame(None)
    c = xml.parse_node(root, f, f, None)
    assert c.GetItemCount() == 2
    for x, item in enumerate([item1, item2]):
        words = item.text.split(', ')
        for y in range(3):
            assert c.GetItem(x, y).Text == words[y]
    f.Destroy()
