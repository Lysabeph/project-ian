#!/usr/bin/python3

#   A database updater that calculates the total amount of time each
#   program has been run for and the number of times each program has
#   been run while the Intuitive Applicaiton Navigator's (I.A.N.) data
#   collection (I.A.N. Monitor) program has been running.
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

import sqlite3
import time

with open("settings.cfg", "r") as settings_file:
    settings_list = settings_file.readlines()

for item in settings_list:

    if "DATABASE=" in item:
        DATABASE = str('='.join(item.rstrip().split('=')[1:]))

# Connects to the database.
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

# Creates an empty array for the unique programs.
programs = []
new_time = str(int(time.time()))

# Reads the last unixepoch time when the update was performed.
with open("latest_time", "r") as file:
    latest_time = file.readline()

# Gets all the unique programs stored in the database.
for record in c.execute("SELECT * FROM Programs;"):
     programs.append(record[1])

# Loops through all the unique programs.
for program in programs:
    c.execute("SELECT ProgramNumber, TotalRunTime, TimesRun FROM Programs WHERE Programs.ProgramName='" + str(program) + "';")
    sqllist = c.fetchone()
    program_number = sqllist[0] # Get the unique number identifier for the program.
    running_time_total = sqllist[1] # Gets the previous total run time.
    counter = sqllist[2] # Gets the previous run counter.

    pstate = None

    # Loops through all the logs recorded after the last update.
    for record in c.execute("SELECT * FROM ProgramLogs WHERE ProgramNumber='" + str(program_number) + "' AND DateTime>'" + latest_time + "' ORDER BY ProgramLogs.DateTime;"):

        # If the previous log was the opening of a program.
        if pstate == "Open":

            # Ignores if the same program is logged to have been opened twice.
            if record[-1] == "Open":
                continue
            # Calculates the time a program was open once the close log is found.
            else:
                ftime = record[-2]
                running_time_total += (int(ftime) - int(stime))
                pstate = "Close"

        # If the previous log was the closing of a program or the start of a new program's logs.
        else:

            # Adds one to the program counter for all open records.
            if record[-1] == "Open":
                stime = record[-2]
                counter += 1
                pstate = "Open"
            # Ignores if the same program is logged to have been closed twice.
            else:
                continue

    # Updates the records of the database with the new information about each program.
    c.execute("UPDATE Programs SET TimesRun='" + str(counter) + "', TotalRunTime='" + str(running_time_total) + "' WHERE Programs.ProgramNumber='" + str(program_number) + "';")

# Commits all changes to the database and closes the connection.
conn.commit()
conn.close()

# Writes the new latest time since update.
with open("latest_time", "w") as file:
    file.write(str(new_time))
