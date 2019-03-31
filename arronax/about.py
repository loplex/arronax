#-*- coding: utf-8-*-

from gi.repository import Gtk, Gio
from gettext import gettext as _
import textwrap
from urllib.parse import urlparse

from . import settings

def add_help_menu(submenu):
    
    menu_item = Gtk.ImageMenuItem(_('Go to Web Page'))
    menu_item.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, 
                                                 Gtk.IconSize.MENU))
    menu_item.connect('activate', on_menuitem_goto_webpage)
    submenu.append(menu_item)

    menu_item = Gtk.SeparatorMenuItem()
    submenu.append(menu_item)

    menu_item = Gtk.ImageMenuItem(_('Ask a Question'))
    menu_item.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, 
                                                 Gtk.IconSize.MENU))
    menu_item.connect('activate', on_menuitem_goto_question_page)
    submenu.append(menu_item)

    menu_item = Gtk.SeparatorMenuItem()
    submenu.append(menu_item)
                   
    menu_item = Gtk.ImageMenuItem(_('Report a Bug'))
    menu_item.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, 
                                                 Gtk.IconSize.MENU))
    menu_item.connect('activate', on_menuitem_bug)
    submenu.append(menu_item)

    menu_item = Gtk.ImageMenuItem(_('Help with Translations'))
    menu_item.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, 
                                                 Gtk.IconSize.MENU))
    menu_item.connect('activate', on_menuitem_translations)
    submenu.append(menu_item)
        
    menu_item = Gtk.ImageMenuItem(_('Donate via Flattr'))
    menu_item.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, 
                                                 Gtk.IconSize.MENU))
    menu_item.connect('activate', on_menuitem_flattr)
    submenu.append(menu_item)

    menu_item = Gtk.ImageMenuItem(_('Donate via PayPal'))
    menu_item.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, 
                                                 Gtk.IconSize.MENU))
    menu_item.connect('activate', on_menuitem_donate)
    submenu.append(menu_item)
    
    submenu.show_all()

def open_url(url):
    u = urlparse(url)
    appinfo=Gio.app_info_get_default_for_uri_scheme(u.scheme)
    appinfo.launch_uris([url], None)

def on_menuitem_about_activate(menuitem):
    about.show_about_dialog()

def on_menuitem_docs(menuitem):
    open_url(settings.LOCAL_DOCS_URL)

def on_menuitem_goto_webpage(menuitem):
    open_url(settings.WEB_URL)

def on_menuitem_goto_question_page(menuitem):
    open_url(settings.QUESTION_URL)

def on_menuitem_donate(menuitem):
    open_url(settings.PAYPAL_URL)

def on_menuitem_flattr(menuitem):
    open_url(settings.FLATTR_URL)

def on_menuitem_translations(menuitem):
    open_url(settings.TRANSLATIONS_URL)

def on_menuitem_bug(menuitem):
    open_url(settings.BUGREPORT_URL)


def show_about_dialog():
    dlg = Gtk.AboutDialog()
    dlg.set_program_name(settings.APP_NAME)
    dlg.set_version(settings.APP_VERSION)
    dlg.set_website('http://www.florian-diesch.de/software/arronax/')
    dlg.set_authors(['Florian Diesch <devel@florian-diesch.de>'])
    dlg.set_wrap_license(True)
    dlg.set_copyright('Copyright (c) 2012 Florian Diesch')
    dlg.set_translator_credits(_("translator-credits"));
    dlg.set_license(textwrap.dedent(
            """
            Arronax - Nautilus plugin to create and modify application starters

            Copyright (c) 2011 Florian Diesch <devel@florian-diesch.de>
           
            Homepage: http://www.florian-diesch.de/software/arronax/
           
            This program is free software: you can redistribute it and/or modify
            it under the terms of the GNU General Public License as published by
            the Free Software Foundation, either version 3 of the License, or
            (at your option) any later version.
           
            This program is distributed in the hope that it will be useful,
            but WITHOUT ANY WARRANTY; without even the implied warranty of
            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
            GNU General Public License for more details.
           
            You should have received a copy of the GNU General Public License
            along with this program.  If not, see <http://www.gnu.org/licenses/>.
            """))

    dlg.run()
    dlg.destroy()


