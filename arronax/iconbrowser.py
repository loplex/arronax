# -*- coding: utf-8 -*-

import os.path
from gi.repository import Gtk, GdkPixbuf

from . import settings, entrytools

class IconDlg():
    def __init__(self, parent):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(settings.GETTEXT_DOMAIN)
      
        self.builder.add_from_file(
            os.path.join(settings.UI_DIR, "icondlg.ui"))
        self.builder.connect_signals(self)
        entrytools.add_clear_button_to_builder_obj(self.builder)
        self.tv = self['tv']
        self.filter = ''

        self['dialog'].set_transient_for(parent)
        
        self.create_list()        
        
    def __getitem__(self, key):
        return self.builder.get_object(key)
    
    def run(self, default):
        dlg = self['dialog']
        dlg.show()
        self.fill_list(default)
        answer = dlg.run()
        name = None
        path, column = self.tv.get_cursor()
        if answer == Gtk.ResponseType.OK and path is not None:
            model = self.tv.get_model()
            name = model[path][1]
        dlg.destroy()
        return name

    def _get_icon_pixbuf(self, theme, name, cache={}):
        if name not in cache:
            pixbuf = theme.load_icon(name, 30,
                        Gtk.IconLookupFlags.FORCE_SIZE|
                        Gtk.IconLookupFlags.USE_BUILTIN)
            cache[name] = pixbuf
        return cache[name]   
        
        
    def create_list(self):
        model = liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        fmodel = model.filter_new(None)
        
        def visifunc(model, iter, data):
            if model[iter]:
                name = model[iter][1]
                return (self.filter == '' or
                        self.filter in name)
            else:
                return True
        fmodel.set_visible_func(visifunc)

        
        self.icon_col = Gtk.TreeViewColumn('Icon')
        self.tv.append_column(self.icon_col)
        self.cell = Gtk.CellRendererPixbuf()
        self.icon_col.pack_start(self.cell, True)
        self.icon_col.add_attribute(self.cell, 'pixbuf', 0)

        self.cell = Gtk.CellRendererText()
        self.icon_col.pack_start(self.cell, True)
        self.icon_col.add_attribute(self.cell, 'text', 1)
        
        self.tv.set_model(fmodel)

    def fill_list(self, current):
        self['swin'].hide()
        self['box_filter'].hide()
        model = self.tv.get_model().get_model()
        self.tv.freeze_notify()
        theme = Gtk.IconTheme.get_default()
        icons = theme.list_icons(None)
        total = float(len(icons))
        pbar = self['progressbar']
        pbar.show()
        select = 0
        for i, name in enumerate(sorted(icons)):
            try:
                pixbuf = self._get_icon_pixbuf(theme, name)
            except Exception as e:
                print((name, e))
                continue
            pos = model.append([pixbuf, name])
            if name == current:
                select = model.get_path(pos)
            if i % 100 == 0:
                pbar.set_fraction(i/total)
                while Gtk.events_pending():
                    Gtk.main_iteration()
        self.tv.set_cursor(select)
        self.tv.thaw_notify()
        pbar.hide()
        self['swin'].show()
        self['box_filter'].show()

   
    def on_e_filter_changed(self, *args):
        self.filter = self['e_filter'].get_text()
        self.tv.get_model().refilter()

