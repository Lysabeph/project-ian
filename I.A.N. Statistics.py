#!/usr/bin/python3

#   A program that calculates the probability that each program will be
#   run  the Intuitive Applicaiton # Navigator's (I.A.N.).
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

import sched
import sqlite3
import time

with open("settings.cfg", "r") as settings_file:
    settings_list = settings_file.readlines()

for setting in settings_list:

    if "TIME_PERIOD=" in setting:
        TIME_PERIOD = int(setting.split("=")[1]) # Default is every day - 86400.

    elif "UPDATE_INTERVAL=" in setting:
        UPDATE_INTERVAL = int(setting.split("=")[1]) # Default is every hour - 3600.

    elif "DATABASE=" in setting:
        DATABASE = str('='.join(setting.rstrip().split('=')[1:]))

print("Time Period:", str(TIME_PERIOD), "Update Interval:", str(UPDATE_INTERVAL))

def get_time_range(epoch):
    current_epoch = epoch
    lower_epoch = current_epoch - current_epoch % UPDATE_INTERVAL
    upper_epoch = lower_epoch + UPDATE_INTERVAL
    return lower_epoch, upper_epoch

def get_specific_probability(variable, dictionary):
    has_run_counter = 0
    c.execute("""
                SELECT Programs.TimesRun
                FROM Programs
                WHERE Programs.ProgramNumber='{0}';
            """.format(str(variable)))

    total_times_run = int(c.fetchone()[0])
    multi_array = []

    for key in dictionary:
        multi_array.append(dictionary[key])

    for array in multi_array:

        if variable in array[0]:
            has_run_counter += 1
            total_times_run += array.count(variable)

    probability = has_run_counter/len(multi_array)
    print(str(variable) + ":", probability, "=", has_run_counter, "/", str(len(multi_array)))
    if (total_times_run/len(multi_array))//1 > 1:
        persistence = 1

    else:
        persistence = 0

    return probability, persistence

def record_remover(program_logs, earliest_epoch):

    for times in list(program_logs.keys()):

        if times < earliest_epoch:
            program_logs.pop(times, None)

def get_statistics(program_logs, program, earliest_epoch, method=1):

    if method == 1:
        print("!", program_logs)
        record_remover(program_logs, earliest_epoch)

        open_logs = dict(program_logs)
        remove_queue = []

        for index in open_logs.keys():
            
            if not open_logs[index][1]:
                remove_queue.append(index)

        for item in remove_queue:
            open_logs.pop(item, None)

        if len(open_logs) < 5:
            return get_statistics(program_logs, program, earliest_epoch, method + 1)

        else:
            probability, persistence = get_specific_probability(program[1], open_logs)

    elif method == 2:
        print("!!")
        record_remover(program_logs, earliest_epoch)
        
        if len(program_logs) < 5:
            return get_statistics(program_logs, program, earliest_epoch, method + 1)

        else:
            probability, persistence = get_specific_probability(program[1], program_logs)

    elif method == 3:
        print("!!!")

        if earliest_epoch + 5*TIME_PERIOD < current_epoch:
            lower_epoch, upper_epoch = get_time_range(current_epoch)
            program_number = 0
            total_number = 0
            
            while upper_epoch > earliest_epoch:
                total_number += 1

                for log in c.execute("""
                            SELECT ProgramLogs.ProgramNumber
                            FROM ProgramLogs
                            WHERE ProgramLogs.OpenClose='Open'
                            AND ProgramLogs.DateTime>='{0}'
                            AND ProgramLogs.DateTime<'{1}';
                        """.format(str(lower_epoch), str(upper_epoch))):

                    if program[1] == log:
                        program_number += 1

                lower_epoch -= UPDATE_INTERVAL
                upper_epoch -= UPDATE_INTERVAL

            probability, persistence = program_number/total_number, 0

    return probability, persistence

conn = sqlite3.connect(DATABASE)
c = conn.cursor()

programs = []

for record in c.execute("""
                            SELECT Programs.ProgramName, Programs.ProgramNumber
                            FROM Programs;
                        """):
    programs.append([record[0], int(record[1])])

open_program_numbers = []
try:
    with open("open_programs", "r") as file:
        open_programs = file.readlines()

except FileNotFoundError:
    open_programs = []

for program in open_programs:
    program = program.split(" ")[0].replace("'", "")

    c.execute("""
            SELECT Programs.ProgramNumber
            FROM Programs
            WHERE Programs.ProgramName='{0}';
        """.format(program))

    open_program_numbers.append(int(c.fetchone()[0]))

current_epoch = 1486190301 # int(time.time())
lower_epoch, upper_epoch = get_time_range(current_epoch)

c.execute("""
            SELECT ProgramLogs.DateTime
            FROM ProgramLogs
            ORDER BY DateTime ASC Limit 1;
        """)
first_epoch = c.fetchone()[0]

print("Programs:", programs, "\nFirst Epoch:", first_epoch)

condition_logs = {} # Will store the programs that have been run with the currently opened programs.

# Separated from the for loop in version 1 to minimise the number of database queries.

while upper_epoch > first_epoch:
    print(lower_epoch, "(lower);", upper_epoch, "(upper)")

    c.execute("""
            SELECT ProgramLogs.OpenClose, ProgramLogs.DateTime
            FROM ProgramLogs
            WHERE ProgramLogs.ProgramNumber=0
            AND ProgramLogs.DateTime<'{0}'
            ORDER BY DateTime DESC Limit 1;
    """.format(str(upper_epoch)))

    open_close = c.fetchone()[0:]
    print(open_close)

    if open_close[0] == "Close":

        if open_close[1] > lower_epoch:
            open_close = "Open"

        else:
            open_close == "Close"

    if open_close == "Open":
        # Similar to logs but resets with each iteration.
        range_logs = []

        for log in c.execute("""
                                SELECT *
                                FROM ProgramLogs
                                WHERE ProgramLogs.OpenClose='Open'
                                AND ProgramLogs.DateTime>='{0}'
                                AND ProgramLogs.DateTime<'{1}';
                            """.format(str(lower_epoch), str(upper_epoch))):
            
            if log[1]:
                range_logs.append(log[1])

        # Checks if the currently open programs have been open togother in the past.
        # This could be done exactly (so no extra programs were open with the current
        # set-up) but this may not be useful.

        program = False # Incase open_programs is empty.

        for program in open_program_numbers:

            if program not in range_logs:
                program = False
                break

        if program:
            condition_logs[upper_epoch] = range_logs, True

        else:
            condition_logs[upper_epoch] = range_logs, False

    lower_epoch -= TIME_PERIOD
    upper_epoch -= TIME_PERIOD

c.execute("""
            UPDATE Programs
            SET Likelihood='0', Persistence='0';
        """)

conn.commit()

for index, program in enumerate(programs):
    program_logs = dict(condition_logs)

    if program[1] in open_program_numbers:
        continue

    c.execute("""
                SELECT ProgramLogs.DateTime
                FROM ProgramLogs
                WHERE ProgramLogs.ProgramNumber='{0}'
                ORDER BY DateTime ASC Limit 1;
            """.format(program[1]))

    earliest_epoch = int(c.fetchone()[0])
    print("Earliest Epoch:", earliest_epoch, "(" + str(program) + ")")

    print(program_logs, program, earliest_epoch)
    probability, persistence = get_statistics(program_logs, program, earliest_epoch)

    programs[index] = [program, probability, persistence]
    print(programs[index])

    c.execute("""
                UPDATE Programs
                SET Likelihood='{0}', Persistence='{1}'
                WHERE Programs.ProgramNumber='{2}';
            """.format(str(probability), str(persistence), str(programs[index][0][1])))

conn.commit()
conn.close()

for program in programs:
    print(program)
