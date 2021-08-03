#!/usr/bin/python3

#   An interface to display and control the output of the Intuitive
#   Applicaiton Navigator's (I.A.N.) data collection (I.A.N. Monitor)
#   and statistical calculation (I.A.N. Statistics.py) programs.
#   
#   Copyright (C) 2017  Elisabeth Morgan
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 3 of the License, or any later
#   version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   The file named LICENSE contains a copy of the GNU General Public
#   License.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import os
import sqlite3
import time

SAVE_PATH = os.getcwd()

with open("settings.cfg", "r") as settings_file:
    settings_text = settings_file.read()

settings_text_list = settings_text.split("\n")

for item in settings_text_list:

    if "DATABASE=" in item:
        DATABASE = str('='.join(item.rstrip().split('=')[1:]))

CONFIG_LIST = {"PREFERRED_NAMES": None, "PREFERRED_COMMANDS": None, "CAPITALISE": None}

for key in CONFIG_LIST:

    if key + "=True" in settings_text:
        CONFIG_LIST[key] = True

    else:
        CONFIG_LIST[key] = False

def reverse_insertion_sort(array, end=None):

    if end is None:
        end = len(array) - 1

    if end >= 1:
        reverse_insertion_sort(array, end - 1)
        number = array[end]
        prev_index = end - 1

        while prev_index >= 0 and array[prev_index][0] < number[0]:
            array[prev_index + 1] = array[prev_index]
            prev_index -= 1

        array[prev_index + 1] = number

    print(array)

def sql_update():
    global conn, c

    sql_programs = []

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    for record in c.execute("""
                SELECT Programs.ProgramName, Programs.PreferredProgramName, ProgramCommands.ProgramCMD, Programs.PreferredCommand, Programs.DisplayProgram, Programs.Likelihood, Programs.Persistence
                FROM Programs, ProgramCommands
                WHERE Programs.ProgramNumber = ProgramCommands.ProgramNumber;
            """):
        record = list(record)

        for index, item in enumerate(record):

            if item == None:
                record[index] = ""

        sql_programs.append(record)

    sorting = []

    for index, data in enumerate(sql_programs):
        sorting.append([data[5], index])

    print(sorting)
    reverse_insertion_sort(sorting)

    for index, data in enumerate(sorting):
        sorting[index] = sql_programs[data[1]]
    print("Sorting:", sorting)

    return sql_programs, sorting

class ButtonGen():

    def on_button_click(self, button):
        os.system(self.command + " &")

    def __init__(self, names, commands, likelihood, persistence):
        self.name = names[0]
        self.command = commands[0]

        if CONFIG_LIST["PREFERRED_NAMES"] and names[1]:
            self.name = names[1]

        if CONFIG_LIST["PREFERRED_COMMANDS"]:
            self.command = commands[1]

        if CONFIG_LIST["CAPITALISE"]:
            self.name = self.name.capitalize()

        self.button = Gtk.Button(label = self.name)
        self.button.connect("clicked", self.on_button_click)

class SettingsButtonGen():

    def __init__(self, names, commands, display):
        self.button_box = Gtk.ButtonBox()
        self.button_box.set_layout(Gtk.ButtonBoxStyle.EXPAND)
        self.button_box.set_spacing(6)

        self.entry_name = Gtk.Entry()
        self.entry_name.set_text(names[1])
        self.entry_command = Gtk.Entry()
        self.entry_command.set_text(commands[1])
        self.checkbutton = Gtk.CheckButton(label=names[0])

        if display:
            self.checkbutton.set_active(True)

        self.button_box.add(self.checkbutton)
        self.button_box.add(self.entry_name)
        self.button_box.add(self.entry_command)

class MainWindow():

    os.chdir(os.environ['HOME'])
    applications_dir = "/usr/share/applications/"
    applications_list = os.listdir(applications_dir)
    gui_applications = []

    for app in applications_list:

        if os.path.isdir(applications_dir + app):
            continue

        with open(applications_dir + app, "r", encoding="utf8") as file:
            app_info = file.read()

        if "Terminal=false" in app_info:
            gui_applications.append(app.split(".")[0])

    gui_applications.sort()
    os.chdir(SAVE_PATH)

    def on_settings_button_click(self, button):
        self.settings_window = SettingsWindow()

    def on_settings_button_mouse_on(self, button):
        self.builder.get_object("settings_button").set_image(self.settings_image_dynamic)

    def on_settings_button_mouse_off(self, button):
        self.builder.get_object("settings_button").set_image(self.settings_image_still)

    def on_run_button_click(self, button):
        self.command = self.builder.get_object("comboboxtext_entry_run").get_text()
        self.builder.get_object("comboboxtext_entry_run").set_text("")
        os.system(self.command + " &")

    def update_interface(self, widget, arg):
        global sql_programs, sorted_sql_programs

        if self.init:
            self.hbox1.destroy()

        self.hbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.builder.get_object("alignment1").add(self.hbox1)
        
        updated_sql_programs, updated_sorted_sql_programs = sql_update()
        print(updated_sorted_sql_programs)

        for program in updated_sorted_sql_programs:

            if program[4]:
                self.button = ButtonGen(program[:2], program[2:4], program[5], program[6])
                self.hbox1.pack_start(self.button.button, False, False, 0)

        self.window.show_all()

        if not self.init:
            self.init = True

    def __init__(self):
        self.init = False
        self.builder = Gtk.Builder()
        self.builder.add_from_file("main.ui")
        self.window = self.builder.get_object("main_window")
        self.window.connect("focus-in-event", self.update_interface)
        self.window.connect("destroy", Gtk.main_quit)

        self.settings_image_dynamic = Gtk.Image()
        self.settings_image_dynamic.set_from_file("icons/cog_dynamic_32x32.gif")
        self.settings_image_still = Gtk.Image()
        self.settings_image_still.set_from_file("icons/cog_still_32x32.png")

        # Gets the widgets.
        self.builder.get_object("settings_button").connect("clicked", self.on_settings_button_click)
        self.builder.get_object("settings_button").connect("enter", self.on_settings_button_mouse_on)
        self.builder.get_object("settings_button").connect("leave", self.on_settings_button_mouse_off)

        self.builder.get_object("run_button").connect("clicked", self.on_run_button_click)

        for self.app in self.gui_applications:
            self.builder.get_object("comboboxtext_run").append_text(self.app)

        self.builder.get_object("comboboxtext_entry_run").connect("activate", self.on_run_button_click)

        self.window.show_all()

class SettingsWindow(Gtk.Window):

    def on_about_click(self, button):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("settings.ui")
        self.about_dialog = self.builder.get_object("aboutdialog")
        self.about_dialog.connect("destroy", self.destroy)
        self.about_dialog.show_all()
        self.about_dialog.run()
        
        self.about_dialog.destroy()

    def error_alert(self, widget, text="Cannot apply changes with a blank field."):
        self.alert = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, text)
        self.alert.run()
        self.alert.destroy()

    def on_apply_changes_button_click(self, button):

        # Prompts an error message box if the database field is left blank.
        if not self.builder.get_object("entry_database").get_text().endswith(".db"):
            self.error_alert("database", "Cannot apply changes until a database file has been selected (.db)")

        elif self.builder.get_object("entry_save_path").get_text() == "":
            self.error_alert("save path")

        else:

            for self.setting in self.settings:

                for self.index, self.item in enumerate(self.settings_list):

                    if self.setting[0] in self.item:

                        if self.setting[2] == 1:
                            self.settings_list[self.index] = self.setting[0] + "=" + str(self.builder.get_object(self.setting[1]).get_value_as_int())

                        elif self.setting[2] == 2:
                            self.settings_list[self.index] = self.setting[0] + "=" + str(self.builder.get_object(self.setting[1]).get_text())

                        elif self.setting[2] == 3:
                            self.settings_list[self.index] = self.setting[0] + "=" + str(self.builder.get_object(self.setting[1]).get_active())

                    else:
                        continue

            with open("settings.cfg", "w") as settings_file:

                for self.item in self.settings_list:

                    if self.item[-1] != "\n":
                        self.item = self.item + "\n"

                    settings_file.write(self.item)

            for program in sql_programs:
                print(program)

                program[1] = program[-1].entry_name.get_text()

                if program[-1].checkbutton.get_active():
                    active = "1"

                else:
                    active = "0"

                c.execute("""
                            UPDATE Programs
                            SET PreferredProgramName='{0}', DisplayProgram='{1}', PreferredCommand='{2}'
                            WHERE ProgramName='{3}';
                        """.format(str(program[1]), str(active), str(program[-1].entry_command.get_text()), str(program[0])))

            conn.commit()

    def on_close_button_click(self, button=None, arg=None):
        self.confirm_dialog = ConfirmDialog(main_window.settings_window.set_window)
        self.close_response = self.confirm_dialog.run()
        self.confirm_dialog.destroy()

        if self.close_response == Gtk.ResponseType.OK:
            main_window.window.set_accept_focus(True)
            self.set_window.destroy()

        else:
            return True

    def on_select_button_click(self, doc):
        self.folder_path = self.dialog.get_current_folder()

        if doc == "folder":
            self.builder.get_object("entry_save_path").set_text(self.folder_path)
            self.builder.get_object("entry_database").set_text("")

        elif doc == "file":
            self.builder.get_object("entry_database").set_text(self.filename)

        for self.index, self.item in enumerate(self.settings_list):

            if "SAVE_PATH" in self.item:
                self.settings_list[self.index] = "SAVE_PATH=" + str(self.folder_path)

            elif "DATABASE" in self.item:
                self.settings_list[self.index] = "DATABASE=" + str(self.filename)

    def on_file_button_click(self, button, doc):

        if doc == "folder":
            self.dialog = Gtk.FileChooserDialog("Open...", self, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
            self.dialog.set_current_folder(self.folder_path)

        elif doc == "file":
            self.dialog = Gtk.FileChooserDialog("Open...", self, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
            self.dialog.set_filename(self.filename)

        self.dialog.set_resizable(False)
        self.dialog.set_transient_for(self.set_window)

        self.dialog.connect("destroy", self.dialog.destroy)

        self.response = self.dialog.run()

        if self.response == Gtk.ResponseType.OK:
            self.on_select_button_click(doc)

        self.dialog.destroy()

    def __init__(self):
        Gtk.Window.__init__(self)
        self.builder = Gtk.Builder()
        self.builder.add_from_file("settings.ui")
        self.set_window = self.builder.get_object("settings_window")
        main_window.window.set_accept_focus(False)
        self.set_window.connect("delete-event", self.on_close_button_click)

        # Reads the settings from the settings.cfg file.
        with open("settings.cfg", "r") as settings_file:
            self.settings_list = settings_file.readlines()

        self.settings = [["UPDATE_TIME", "spinbutton_update_time", 1], ["SAVE_PATH", "entry_save_path", 2], ["DATABASE", "entry_database", 2], ["TIME_PERIOD", "spinbutton_time_period", 1], ["UPDATE_INTERVAL", "spinbutton_update_interval", 1], ["PREFERRED_NAMES", "checkbutton_preferred_names", 3], ["PREFERRED_COMMANDS", "checkbutton_preferred_commands", 3], ["CAPITALISE", "checkbutton_capitalise", 3]]

        for self.setting in self.settings:

            for self.item in self.settings_list:

                if self.setting[0] in self.item:

                    if self.setting[2] == 1:
                        self.builder.get_object(self.setting[1]).set_value(int('='.join(self.item.rstrip().split('=')[1:])))

                    elif self.setting[2] == 2:
                        self.builder.get_object(self.setting[1]).set_text('='.join(self.item.rstrip().split('=')[1:]))

                    elif self.setting[2] == 3:

                        if "True" in self.item:
                            self.builder.get_object(self.setting[1]).set_active(True)

                        elif "False" in self.item:
                            self.builder.get_object(self.setting[1]).set_active(False)

                else:
                    continue

        self.folder_path = self.builder.get_object("entry_save_path").get_text()
        self.filename = self.builder.get_object("entry_database").get_text()

        for self.index, self.program in enumerate(sql_programs):

            sql_programs[self.index].append(SettingsButtonGen(self.program[:2], self.program[2:4], self.program[4]))
            self.builder.get_object("box_programs").pack_start(self.program[-1].button_box, False, False, 0)

        self.builder.get_object("button_save_path").connect("clicked", self.on_file_button_click, "folder")
        self.builder.get_object("button_database").connect("clicked", self.on_file_button_click, "file")
        self.builder.get_object("apply_changes_button1").connect("clicked", self.on_apply_changes_button_click)
        self.builder.get_object("close_button1").connect("clicked", self.on_close_button_click)
        self.builder.get_object("about_button").connect("clicked", self.on_about_click)

        self.set_window.show_all()

class ConfirmDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Close...", parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Close", Gtk.ResponseType.OK))
        self.parent = parent
        self.set_resizable(False)
        self.set_transient_for(main_window.settings_window.set_window)

        self.close_label = Gtk.Label()
        self.close_label.set_markup("<big><b>Are you sure you're done?</b></big>")
        self.advice_label = Gtk.Label("You must click 'Apply Changes' in order for your settings to be saved.")
        self.advice_label.set_line_wrap(True)
        self.advice_label.set_alignment(xalign=0.5, yalign=0.5)
        self.box = self.get_content_area()
        self.box.set_orientation(Gtk.Orientation.VERTICAL)
        self.box.set_spacing(6)
        self.box.pack_start(self.close_label, False, False, 0)
        self.box.pack_start(self.advice_label, False, False, 0)
        self.show_all()

sql_programs, sorted_sql_programs = sql_update()

main_window = MainWindow()
Gtk.main()

