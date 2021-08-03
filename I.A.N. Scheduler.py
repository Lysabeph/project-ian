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

os.system("chmod +x I.A.N.\ Monitor")

s = sched.scheduler(time.time, time.sleep)

def updater():
    os.system("python3 I.A.N.\ Log\ Updater.py &")

def program_scheduler():
    s.enter(3600, 1, updater)
    s.run()
    
    return True

updater()
os.system("python3 I.A.N.\ Interface.py")
os.system("./I.A.N.\ Monitor &")
t = 3540 - int(time.time())%3600

if t > 0:
    time.sleep(t)
    
updater()
while True:
    program_scheduler()
