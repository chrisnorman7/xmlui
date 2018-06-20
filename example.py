"""Show a frame generated from an XML file."""

from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
import wx
from xmlui.wx import WXXMLParser


class MyXMLParser(WXXMLParser):
    """Add event handlers."""

    def on_paste(self, event):
        """Pop up an alert."""
        return wx.MessageBox('You shouldn\'t copy and paste passwords.')

    def on_copy(self, event):
        """Pop up an alert."""
        return wx.MessageBox(
            'You probably won\'t get any useful text that way.'
        )

    def on_login(self, event):
        frame = event.GetEventObject().GetParent().GetParent()
        username = frame.username.GetValue()
        password = frame.password.GetValue()
        return wx.MessageBox(
            'You clicked the Login button.\n\n'
            f'Username: {username}\n'
            f'Password: {password}'
        )

    def close(self, event):
        event.GetEventObject().GetParent().GetParent().Close(True)


parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
xml = MyXMLParser()

parser.add_argument(
    'filename', nargs='?', type=FileType('r'), default='frame.xml',
    help='The file to load'
)


def main(args):
    a = wx.App()
    f = wx.Frame(None)
    xml.populate_from_file(args.filename, f, None)
    f.Show(True)
    f.Maximize()
    a.MainLoop()


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
