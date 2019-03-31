# -*- coding: utf-8 -*-

from gi.repository import Gtk, GdkPixbuf

import os.path
from . import settings, tvtools

from gettext import gettext as _


all_categories = [
    'Audio', 'Video', 'Development',
    'Education', 'Game', 'Graphics',
    'Network', 'Office', 'Science',
    'Settings', 'System', 'Utility'
    ]

class CategoriesDlg():
    def __init__(self, parent, categories):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(settings.GETTEXT_DOMAIN)
      
        self.builder.add_from_file(
            os.path.join(settings.UI_DIR, "categoriesdlg.ui"))
        self.builder.connect_signals(self)
        self['dialog'].set_transient_for(parent)

        self.categories = categories
        self.create_tv()
        
        
    def __getitem__(self, key):
        return self.builder.get_object(key)

    def create_tv(self):
        tv = self['tv']
        model =  Gtk.ListStore(bool, str)
        tv.set_model(model)

        col, rend = tvtools.create_treeview_column(tv, _('Selected'),
            col_no=0, attr='active', renderer=Gtk.CellRendererToggle(),
            activatable=True)
        def callback(renderer, path):
            model = tv.get_model()
            model[path][0] = not model[path][0]
        rend.connect('toggled', callback)

        tvtools.create_treeview_column(
            tv, 'Category', col_no=1, is_sort_col=True)

        for cat in set(all_categories+self.categories):
            model.append([cat in self.categories, cat])
        
        
    def get_selected_categories(self):
        model = self['tv'].get_model()
        return sorted(name for selected, name in model if selected)
        
    def run(self):
        dlg = self['dialog']
        dlg.show()
        answer = dlg.run()
        if answer == Gtk.ResponseType.OK:
            selected = self.get_selected_categories()
        else:
            selected = None
        dlg.destroy()
        return selected

