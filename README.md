# xmlui
Create user interfaces from XML files

## What is it?
This module allows you to create whole user interfaces writing nothing but XML, allowing you to lever the power of existing modules like jinja2 to include xml files in other xml files, allowing you to create things like a playback controls bar for example, and have that show up in multiple windows.

## How it works
For an example, see the `example.py` and `frame.xml` files.

### Tags
By default, the base xml parser (`xmlui.base.XMLParser`) doesn't support any tags. These are added in subclasses. This is because xmlui is backend-agnostic. It doesn't care if you are using [wxPython](https://www.wxpython.org/), or [Tkinter](https://wiki.python.org/moin/TkInter).

To add a tag, subclass `xmlui.base.XMLParser` and code a method with the name of the tag, preceded by parse_.

The only reserved attribute name is `name`. This is used for adding controls to frames with setattr.

For example:

```
<tag name="tag">This is a tag</tag>
```

Would be added to the frame with the name tag.

There are a couple of helper methods you can use while creating methods. These are listed below.

#### get_list
This method allows you to generate a list from a string.

Given a string like `1, 2, 3`, `get_string` would yield: `[1, 2, 3]`.

##### Arguments
* text: The text to break up into the list.
* start: The initial list. Defaults to the empty list.
* function: The function to apply to each chunk of the list. Defaults to int.

### Implementations
The only implementation at present is that for wx. Supported tags are described below.

#### Overview
The `parse_node` method - which is responsible for parsing each node - does a couple of useful things by default, and as such, almost all tags can have special attributes.

* label: Pased to `control.SetLabel`.
* style: Passed to `control.SetWindowStyle`. This flag will be handled by parse_table (which yields a `wx.ListCtrl instance), because of the way that control requires certain styles to be in place in order for columns to work.
* size: Passed to `control.SetSize`.
* binders: A comma-separated list of event:method pairs. For example: `binders="evt_button:onclick"` would be the same as `control.Bind(wx..EVT_BUTTON, xml.onclick)`, where `xml` is the instance of `WXXMLParser` being used, and `control` is the created control.

#### title
Set the title for a frame.

##### Example
```
<title>This is a frame</title>
```

#### sizer
Create sizers.

##### Example
```
<sizer>
    <element1></element1>
    <element2></element2>
    ...
</sizer>
```

This node may contain subnodes which will be automatically added to the sizer.

##### Arguments

###### orient
The only argument passed to `wx.BoxSizer.__init__`. Defaults to 'horizontal'.

#### label
Create `wx.StaticText` instances.

##### Example
```
<label>This is a &nbsp;Label</label>
```

##### Arguments
None

#### text
Create `wx.TextCtrl` instances.

##### Example
```
<text>This is the text in the control.</text>
```

##### Arguments
None

#### integer
Create `wx.lib.intctrl.IntCtrl` instances.

##### Example
```
<integer min="0" max="100">50</integer>
```

##### Arguments
* min: The minimum value.
* max: The maximum value.
* limited: Used by `IntCtrl.GetLimited` and `IntCtrl.SetLimited`.
* allow_none: Used by `IntCtrl.IsNoneAllowed` and `IntCtrl.SetIsNoneAllowed`.
` allow_long: Used by `IntCtrl.IsLongAllowed` and `IntCtrl.SetIsLongAllowed`.

#### float
This tag is used to create `wx.lib.agw.floatspin.FloatSpin` instances."

##### Example
```
<float min="0.0" max="100.0" increment="0.5" digits="2">50.0</float>
```

##### Arguments
* min: The miminum value.
* max: The maxim um value.
* increment: How much the control is altered by the arrow keys.
* digits: The number of digits to show.

#### slider
Create `wx.Slider` instances.

##### Example
```
<slider min="0" max="100">50</slider>
```

##### Arguments
* min: The minimum value.
* max: The maximum value.

#### checkbox
Create `wx.CheckBox` instances.

##### Example
```
<checkbox>1</checkbox>
```

The value of the checkbox is given as an integer, 0 or 1.

##### Arguiments
None

#### button
Create `wx.Button` instances.

##### Example
```
<button default="1">&nbsp;Button</button>
```

If default is given and is non-0, then `button.SetDefault()` will be called.

##### Arguments
* default: Whether or not to set this button as the default.

#### choice
Create `wx.Choice` instances.

##### Example
```
<choice choices="choice1, choice2, ...">0</choice>
```

If value is given then it is converted to an integer, and passed to `wx.Choice.SetSelection`.

##### Arguments
* choices: A comma-separated list of strings.

#### list
Created `wx.ListBox` instances.

##### Example
```
<list choices="choice1, choice2, ...>0</list>
```

If value is given then it is converted to an integer, and passed to `wx.ListBox.SetSelection`.

##### Arguments
* choices: A comma-separated list of strings.

#### table
Create `wx.ListCtrl` instances.

##### Example
```
<table>
    <column>First Column Header</column>
    <column>Second Column Header</column>
    ...
    <item>Item1: Col1, Item1: Col2,...</item>
    <item>Item2: Col1, Item2: Col2,...</item>
    <value>0</value>
</table>
```

The table tag can contain 0 or more column child tags, 0 or more item child tags, and technically 0 or more value child tags, although only 1 value tag will ever be used (the last one).

Any other tag raises `xmlui.wx.InvalidTagError`.

##### Arguments
* Style: Although this is a global attribute, it is mentioned again here because if you plan to use columns, you must also provide the style attribute as `"lc_report"`.

#### column
Used by the `table` tag to create columns.]

##### Example
```
<column format="list_format_left" width="-1">Column Header</column>
```

If no value is given, then `xmlui.wx.NoValueError` is raised.

##### Arguments
* format: One of the members of `wx.ListColumnFormat`.
* width: The width of the column.

#### item
Used by the `table` tag to create list items.

##### Example
```
<item>col1, col2, ...</item>
```

Value must be given as an integer, unless `xmlui.wx.WXXMLParser.parse_value` is overridden.

##### Arguments
None
