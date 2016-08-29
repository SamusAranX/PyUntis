#!/usr/bin/env python3
#-*- coding: utf-8 -*-
from urllib.parse import urlencode
from datetime import datetime, timedelta, date
import sys
import os
import math
import json
import icu, locale # This ensures that lists with non-ASCII characters will still be properly sorted
from calendar import day_name, day_abbr
from PyUntisClasses import *
from PyUntisSession import PyUntisSession

# http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)
        
# A weekday index of 0, together with a week index of 0, will get you this week's monday.
# A weekday index of 4 would get you this week's friday.
# A week index of 1 would get you next week's monday or friday and so on.
def get_other_weekday(weekday_index, week_index, start_day=None):
    day = start_day.date if start_day else datetime.now()
    new_date = day - timedelta(days = day.weekday()) + timedelta(days = weekday_index) + timedelta(days = week_index * 7)
    return PyUntisDate(date=new_date)
    
# In case your school doesn't give your Untis account
# the privileges necessary to use getTeachers(),
# you can use this workaround.
# Of course, this requires that you have a way to connect
# teacher IDs to their names, for example by cross-referencing
# the IDs the API returns and the names your school's
# in-house substitution plan displays.
def load_teachers_from_file(f):
    with open(f, "r", encoding="utf-8") as t_file:
        t_json = json.load(t_file)
        t_keys = sorted(t_json.keys(), key=int)
        t_list = [{
            "id": key,
            "name": t_json[key]
        } for key in t_keys]
        
        return [PyUntisTeacher(t) for t in t_list]
    
# len(box_chars) MUST be an odd number
# "╔╦═╦╗" is a valid box_chars string, for example
# 0 is left, 1 is center, 2 is right
def box_print(box_chars, str="", mode=1):
    OUTPUT_WIDTH = 50
    assert len(box_chars) % 2 == 1
    c_start = len(box_chars) // 2
    c_end = math.ceil(len(box_chars) / 2)
    chars_start = box_chars[:c_start]
    chars_end = box_chars[c_end:]
    char_center = box_chars[c_start:c_end]
    
    transformed_str = ""
    if mode == 1:
        transformed_str = str.center(OUTPUT_WIDTH - len(chars_start + chars_end), char_center)
    elif mode == 0:
        transformed_str = str.ljust(OUTPUT_WIDTH - len(chars_start + chars_end), char_center)
    elif mode == 2:
        transformed_str = str.rjust(OUTPUT_WIDTH - len(chars_start + chars_end), char_center)
        
    print(chars_start + transformed_str + chars_end)
    

tick = datetime.now()

s = PyUntisSession()

box_print("╔╦═╦╗")
box_print("║║ ║║", "{0} - {1}".format(s.USER_AGENT.upper(), tick.strftime("%d.%m.%Y %H:%M:%S")))
box_print("╠╩═╩╣")

box_print("║   ║", "Loading config…", 0)

config_json = open("config.json", "r", encoding="utf8")
config = json.load(config_json)
config_json.close()

box_print("║   ║", "Loaded.", 0)

plan_dir = config["plan_dir"]
os.makedirs(plan_dir, exist_ok=True)

collator = icu.Collator.createInstance(icu.Locale(config["locale"]))

box_print("║   ║", "Looking for school and authenticating…", 0)

schools = s.searchSchools(config["school"]["name"])
assert len(schools) >= 1, "Can't find school"

auth = s.authenticate(schools[0], config["school"]["username"], config["school"]["password"])

box_print("║   ║", "Authenticated.", 0)
box_print("╠═╣", "meta.json".upper())

#####
# Part where we create meta.json
#####

box_print("║   ║", "Setting up date formats…", 0)

# Set up the object itself, along with full and small date formats
meta = {}
meta_full = "{0}|{1}"
meta_small = "{0}.,|{1}"

# Get the first days of this week and the next two weeks
week1_mon = get_other_weekday(weekday_index = 0, week_index = 0)
week2_mon = get_other_weekday(weekday_index = 0, week_index = 1)
week3_mon = get_other_weekday(weekday_index = 0, week_index = 2)

# Add date display formats to meta object
meta["week1Full"] = [meta_full.format(day_name[w], (week1_mon.date + timedelta(days = w)).strftime("%d.%m.%Y")) for w in range(0,5)]
meta["week2Full"] = [meta_full.format(day_name[w], (week2_mon.date + timedelta(days = w)).strftime("%d.%m.%Y")) for w in range(0,5)]
meta["week3Full"] = [meta_full.format(day_name[w], (week3_mon.date + timedelta(days = w)).strftime("%d.%m.%Y")) for w in range(0,5)]
meta["week1Small"] = [meta_small.format(day_abbr[w], (week1_mon.date + timedelta(days = w)).strftime("%d.%m.")) for w in range(0,5)]
meta["week2Small"] = [meta_small.format(day_abbr[w], (week2_mon.date + timedelta(days = w)).strftime("%d.%m.")) for w in range(0,5)]
meta["week3Small"] = [meta_small.format(day_abbr[w], (week3_mon.date + timedelta(days = w)).strftime("%d.%m.")) for w in range(0,5)]


# Add school year information to meta object
box_print("║   ║", "Requesting school year information…", 0)
current_schoolyear = s.getCurrentSchoolyear()
meta["currentSchoolyear"] = {
    "name": current_schoolyear.name,
    "startDate": current_schoolyear.start_date.make_readable(),
    "endDate": current_schoolyear.end_date.make_readable(),
    "startDateUntis": current_schoolyear.start_date.untis_date,
    "endDateUntis": current_schoolyear.end_date.untis_date
}

# Add holiday information to meta object
box_print("║   ║", "Requesting holiday information…", 0)
holidays = s.getHolidays()
meta["holidays"] = [
    {
        "name": h.long_name,
        "startDate": h.start_date.make_readable(),
        "endDate": h.end_date.make_readable(),
        "startDateUntis": h.start_date.untis_date,
        "endDateUntis": h.end_date.untis_date
    } for h in holidays
]
    
# Add school classes and IDs to meta object
box_print("║   ║", "Requesting class information…", 0)
classes = s.getKlassen()
classes_sorted = sorted(classes, key=lambda kl: collator.getSortKey(kl.name.lower()))
meta["classes"] = {
    "names": [kl.name for kl in classes_sorted],
    "ids": [kl.id for kl in classes_sorted],
    "length": len(classes_sorted)
}

# Add teachers to meta object
box_print("║   ║", "Requesting teacher information…", 0)
# teachers = s.getTeachers()
teachers = load_teachers_from_file("teachers.json")
meta["teachers"] = {}
for t in teachers:
    meta["teachers"][t.id] = t.name
    
box_print("║   ║", "Requesting timegrid information…", 0)
timegrid = s.getTimegridUnits()
meta["timegrid"] = []
for tg in timegrid:
    meta["timegrid"].insert(tg.day, tg.to_json())

box_print("║   ║", "Adding last update times…", 0)
meta["lastUpdated"] = s.getLatestImportTime().strftime("%d.%m.%Y %H:%M:%S")
meta["lastGenerated"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

box_print("║   ║", "Writing meta.json…", 0)
with open(os.path.join(plan_dir, "meta.json"), mode="w", encoding="utf-8") as meta_file:
    # meta_file.write(json.dumps(meta, ensure_ascii = False))
    meta_file.write(json.dumps(meta, ensure_ascii = False, indent = 2))
    box_print("║   ║", "Done.", 0)
    
#####
# Part where we create timetable files for the web interface
#####
    
box_print("╠═╣", "Timetable JSON files".upper())

box_print("║   ║", "Requesting substitution data…", 0)
substitutions = s.getSubstitutions(start_date = "20160824", end_date = "20160826")

for kl in [k for k in classes if k.id == 301]:
    box_print("║   ║", "Requesting timetables for {0}…".format(kl), 0)
    week3_fri = get_other_weekday(weekday_index = 4, week_index = 2) # Get the last school day of the week after next
    
    # Clamp start and end dates. If one of these dates lies 
    clamped_start_date = str(max(int(current_schoolyear.start_date.untis_date), int(week1_mon.untis_date)))
    clamped_end_date = str(min(int(current_schoolyear.end_date.untis_date), int(week3_fri.untis_date)))
    
    timetable = s.getTimetableCustom(kl.id, PyUntisElementType.CLASS, 
        start_date = clamped_start_date, end_date = clamped_end_date,
        showInfo = True, showSubstText = True, showLsText = True, showLsNumber = True, showStudentgroup = True)
        
    timetable_days = sorted(list(set([t.date for t in timetable])))
    
    timetable_json = {}
    for date in timetable_days:
        day_lessons = sorted([t for t in timetable if t.date == date], key=lambda l: l.start_time)
        date_timeunits = timegrid[date.date.weekday()]
        for lesson in day_lessons:
            print(next(tu for tu in date_timeunits if tu.start_time == lesson.start_time))
            
        sys.exit(0)
            

box_print("║   ║", "Logging out.", 0)
s.logout()

tock = datetime.now()
diff = tock - tick
box_print("╠╦═╦╣")
box_print("║║ ║║", "Finished in {0}".format(diff))
box_print("╚╩═╩╝")