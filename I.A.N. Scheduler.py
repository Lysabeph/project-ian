#!/usr/bin/python3

#   A scheduler for the sub-programs of the Intuitive Applicaiton
#   Navigator's (I.A.N.).
#
#   Copyright (C) 2017  Elisabeth Morgan
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
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

import os
import sched
import time

with open("settings.cfg", "r") as settings_file:
    settings_list = settings_file.readlines()

for setting in settings_list:

    if "UPDATE_INTERVAL=" in setting:
        UPDATE_INTERVAL = int(setting.split("=")[1]) # Default is every hour - 3600.
        break

os.system("chmod +x I.A.N.\ Monitor")

s = sched.scheduler(time.time, time.sleep)

def updater():
    os.system("python3 I.A.N.\ Log\ Updater.py &")
    os.system("python3 I.A.N.\ Statistics.py &")

def program_scheduler():
    s.enter(UPDATE_INTERVAL, 1, updater)
    s.run()

    return True

updater()
os.system("python3 I.A.N.\ Interface.py")
os.system("./I.A.N.\ Monitor &")
t = (UPDATE_INTERVAL - 60) - int(time.time())%UPDATE_INTERVAL

if t > 0:
    time.sleep(t)

updater()

while True:
    program_scheduler()
