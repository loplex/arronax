#-*- coding: utf-8-*-
from gi.repository import Gtk, GdkPixbuf, GLib

statusbar = None

DELAY = 3000

class Status(object):

    def __init__(self, msg=None, end_msg=None, delay=DELAY):
        self.msg = msg
        self.end_msg = end_msg
        self.delay = delay
        self.context = statusbar.get_context_id('')


    def set_end_msg(self, msg):
        self.end_msg = msg
        
    def __enter__(self):
        if self.msg is not None:
            statusbar.push(self.context, self.msg)
        return self

    def __exit__(self, *args):
        if self.end_msg is not None:
            statusbar.pop(self.context)
            statusbar.push(self.context, self.end_msg)
        GLib.timeout_add(self.delay, 
                         lambda *args: statusbar.pop(self.context))

            

def show_msg(msg, delay=DELAY):
    context = statusbar.get_context_id('')
    if msg is not None:
        statusbar.push(context, msg)
        GLib.timeout_add(delay, 
                         lambda *args: statusbar.pop(context))



def init(widget):
    global statusbar    
    statusbar = widget


