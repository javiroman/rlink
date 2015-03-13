#!/usr/bin/env python
"""
rlinkview.py - Rlink front end viewer.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
version 3 as published by the Free Software Foundation.

(c) 2010 Javi Roman <javiroman@kernel-labs.org>

$Id$
"""
import wxversion 
wxversion.select("2.8")
import wx
import wx.html
from wx.lib.wordwrap import wordwrap
import sys
import os
import time
import Ice

# project package imports
for module in ['project', 'utils', 'images']:
    pkg = __import__(sys.argv[0].split(".")[0] + "." + module)

class CustomStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)

        # This status bar has three fields
        self.SetFieldsCount(3)
        # Sets the three fields to be relative widths to each other.
        self.SetStatusWidths([-2, -1, -2])
        self.sizeChanged = False
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # Field 0 ... just text
        self.SetStatusText("A Custom StatusBar...", 0)

        # This will fall into field 1 (the second field)
        self.cb = wx.CheckBox(self, 1001, "toggle clock")
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleClock, self.cb)
        self.cb.SetValue(True)

        # set the initial position of the checkbox
        self.Reposition()

        # We're going to use a timer to drive a 'clock' in the last
        # field.
        self.timer = wx.PyTimer(self.Notify)
        self.timer.Start(1000)
        self.Notify()

    # Handles events from the timer we started in __init__().
    # We're using it to drive a 'clock' in field 2 (the third field).
    def Notify(self):
        t = time.localtime(time.time())
        st = time.strftime("%d-%b-%Y   %I:%M:%S", t)
        self.SetStatusText(st, 2)


    # the checkbox was clicked
    def OnToggleClock(self, event):
        if self.cb.GetValue():
            self.timer.Start(1000)
            self.Notify()
        else:
            self.timer.Stop()

    def OnSize(self, evt):
        self.Reposition()  # for normal size events

        # Set a flag so the idle time handler will also do the repositioning.
        # It is done this way to get around a buglet where GetFieldRect is not
        # accurate during the EVT_SIZE resulting from a frame maximize.
        self.sizeChanged = True

    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()

    # reposition the checkbox
    def Reposition(self):
        rect = self.GetFieldRect(1)
        self.cb.SetPosition((rect.x+2, rect.y+2))
        self.cb.SetSize((rect.width-4, rect.height-4))
        self.sizeChanged = False

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, 
                          pos=(150,150), size=(640,600),
                          style=wx.DEFAULT_FRAME_STYLE)
        self.Center()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Menu bar: fixed positon
        menuBar = wx.MenuBar()

        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")

        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)

        # Tool bar: fixed position
        toolbar = self.CreateToolBar()
        toolbar.AddSimpleTool(wx.NewId(), pkg.images.exit.GetBitmap(),
                              "New", "Long help for 'New'")
        toolbar.Realize()

        # Status bar: fixed position
        self.statusbar = CustomStatusBar(self)
        self.SetStatusBar(self.statusbar)

        # Central panel
        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        m_text = wx.StaticText(panel, -1, "Hello World!")
        m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        m_text.SetSize(m_text.GetBestSize())
        box.Add(m_text, 0, wx.ALL, 10)

        m_close = wx.Button(panel, wx.ID_CLOSE, "Close")
        m_close.Bind(wx.EVT_BUTTON, self.OnClose)
        box.Add(m_close, 0, wx.ALL, 10)

        panel.SetSizer(box)
        panel.Layout()

    def OnClose(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()

        info.Name = pkg.project.__project__
        info.Version = pkg.project.__version__
        info.Copyright = pkg.project.copyrightText
        info.Description = wordwrap(pkg.project.aboutText, 350, wx.ClientDC(self))
        info.WebSite = pkg.project.website
        info.Developers = pkg.project.developers
        info.License = wordwrap(pkg.project.licenseText, 500, wx.ClientDC(self))
        
        wx.AboutBox(info)

    def SelectRlinkServer(self):
        """We've to select an user, remote rlink server, because
            this application is only for each server running.
        """
        choices = ["user10000", "user10001", "user10002", "user10003",
            "user10004", "user10005", "user10006", "user10007",
            "user10008", "user10009", "user33333"]

        dialog = wx.SingleChoiceDialog(None, "Selecciona un usuario", 
                "Usuarios disponibles", choices)
        if dialog.ShowModal() == wx.ID_OK:
            print "You selected: %s\n" % dialog.GetStringSelection()
        dialog.Destroy()

class MySplashScreen(wx.SplashScreen):
    def __init__(self):
        bmp = wx.Image(pkg.utils.opj("rlinkview/splash.png")).ConvertToBitmap()
        wx.SplashScreen.__init__(self, bmp,
                                 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                                 5000, None, -1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.fc = wx.FutureCall(2000, self.ShowMain)

    def OnClose(self, evt):
        # Make sure the default handler runs too so this window gets
        # destroyed
        evt.Skip()
        self.Hide()

        # if the timer is still running then go ahead and show the
        # main frame now
        if self.fc.IsRunning():
            self.fc.Stop()
            self.ShowMain()

    def ShowMain(self):
        frame = MainFrame(None, pkg.project.__project__)
        frame.Show()
        if self.fc.IsRunning():
            self.Raise()

        wx.CallAfter(frame.SelectRlinkServer)

class ProjectApp(wx.App):

    def OnInit(self):
        # Version sanity check
        if pkg.project.VERSION_STRING != wx.VERSION_STRING:
            wx.MessageBox(caption="Warning",
                          message="You're using version %s of wxPython, \n"
                          "but this application was written for version %s.\n"
                          "There may be some version incompatibilities..."
                          % (wx.VERSION_STRING, VERSION_STRING))

        splash = MySplashScreen()
        splash.Show()

        return True

def main():
    # system tools sanity check
    for exefile in pkg.project.minimal_tools:
        if not pkg.utils.which(os.getenv("PATH"), exefile):
            print "sorry, you have to install %s utility" % exefile
            sys.exit(1)

    app = ProjectApp()
    app.MainLoop()

if __name__=="__main__":
    sys.exit(main())

# vim: ts=4:sw=4:et:sts=4:ai:tw=80

