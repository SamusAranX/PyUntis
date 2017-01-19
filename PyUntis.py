#coding=utf-8
from urllib.parse import urlencode
from datetime import datetime, timedelta, date
import sys
import os
import math
import json
import locale # This ensures that lists with non-ASCII characters will still be properly sorted
from calendar import day_name, day_abbr
from PyUntisClasses import *
from PyUntisSession import PyUntisSession

# Modified from http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
def daterange(start_date, end_date):
    # Add a day to end_date to make it inclusive
    for n in range(int((end_date + timedelta(days = 1) - start_date).days)):
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
def box_print(box_chars, str="", align="left"):
    OUTPUT_WIDTH = 50
    assert len(box_chars) % 2 == 1
    c_start = len(box_chars) // 2
    c_end = math.ceil(len(box_chars) / 2)
    chars_start = box_chars[:c_start]
    chars_end = box_chars[c_end:]
    char_center = box_chars[c_start:c_end]
    
    transformed_str = ""
    if align == "left":
        transformed_str = str.ljust(OUTPUT_WIDTH - len(chars_start + chars_end), char_center)
    elif align == "center":
        transformed_str = str.center(OUTPUT_WIDTH - len(chars_start + chars_end), char_center)
    elif align == "right":
        transformed_str = str.rjust(OUTPUT_WIDTH - len(chars_start + chars_end), char_center)
    else:
        raise ValueError("align must either be \"left\", \"center\" or \"right\".")
        
    print(chars_start + transformed_str + chars_end)
    
tick = datetime.now()

s = PyUntisSession()

box_print("╔╦═╦╗")
box_print("║║ ║║", "{0} - {1}".format(s.USER_AGENT.upper(), tick.strftime("%d.%m.%Y %H:%M:%S")), "center")
box_print("╠╩═╩╣")

box_print("║   ║", "Loading config…")

config_json = open("config.json", "r", encoding="utf8")
config = json.load(config_json)
config_json.close()

try:
	locale.setlocale(locale.LC_ALL, config["locale"])
except:
	box_print("║   ║", "Unsupported locale: " + config["locale"])

box_print("║   ║", "Loaded.")

plan_dir = config["plan_dir"]
os.makedirs(plan_dir, exist_ok=True)

try:
    import icu
    collator = icu.Collator.createInstance(icu.Locale(config["locale"]))
except ImportError:
    box_print("║   ║", "Install PyICU for better list sorting.")

box_print("║   ║", "Looking for school and authenticating…")

schools = s.searchSchools(config["school"]["name"])
assert len(schools) >= 1, "Can't find school"

auth = s.authenticate(schools[0], config["school"]["username"], config["school"]["password"])

box_print("║   ║", "Authenticated.")
box_print("╠═╣", "meta.json".upper(), "center")

#####
# Part where we create meta.json
#####

box_print("║   ║", "Setting up date formats…")

# Set up the object itself, along with full and small date formats
meta = {}
meta_long = "{0}<br>{1}"
meta_short = "{0}.,<br>{1}"

# Get the first days of this week and the next two weeks
week1_mon = get_other_weekday(weekday_index = 0, week_index = 0)
week2_mon = get_other_weekday(weekday_index = 0, week_index = 1)
week3_mon = get_other_weekday(weekday_index = 0, week_index = 2)

# Add date display formats to meta object
meta["weekDatesLong"] = []
meta["weekDatesShort"] = []
meta["weekDatesLong"].append([meta_long.format(day_name[w], (week1_mon.date + timedelta(days = w)).strftime("%d.%m.%Y")) for w in range(0,5)])
meta["weekDatesLong"].append([meta_long.format(day_name[w], (week2_mon.date + timedelta(days = w)).strftime("%d.%m.%Y")) for w in range(0,5)])
meta["weekDatesLong"].append([meta_long.format(day_name[w], (week3_mon.date + timedelta(days = w)).strftime("%d.%m.%Y")) for w in range(0,5)])
meta["weekDatesShort"].append([meta_short.format(day_abbr[w], (week1_mon.date + timedelta(days = w)).strftime("%d.%m.")) for w in range(0,5)])
meta["weekDatesShort"].append([meta_short.format(day_abbr[w], (week2_mon.date + timedelta(days = w)).strftime("%d.%m.")) for w in range(0,5)])
meta["weekDatesShort"].append([meta_short.format(day_abbr[w], (week3_mon.date + timedelta(days = w)).strftime("%d.%m.")) for w in range(0,5)])

# Add school year information to meta object
box_print("║   ║", "Requesting school year information…")
current_schoolyear = s.getCurrentSchoolyear()
meta["currentSchoolyear"] = current_schoolyear.to_json()

# Add holiday information to meta object
box_print("║   ║", "Requesting holiday information…")
holidays = s.getHolidays()
meta["holidays"] = [h.to_json() for h in holidays]

# Add school classes and IDs to meta object
box_print("║   ║", "Requesting class information…")
classes = s.getKlassen()
try:
    classes_sorted = sorted(classes, key=lambda kl: collator.getSortKey(kl.name.lower()))
except NameError:
    classes_sorted = sorted(classes, key=lambda kl: kl.name.lower())
    
meta["classes"] = {
    "names": [kl.name for kl in classes_sorted],
    "ids": [kl.id for kl in classes_sorted],
    "length": len(classes_sorted)
}

# Add teachers to meta object
box_print("║   ║", "Requesting teacher information…")
# teachers = s.getTeachers()
teachers = load_teachers_from_file("teachers.json")
meta["teachers"] = {}
for t in teachers:
    meta["teachers"][t.id] = t.name
    
box_print("║   ║", "Requesting timegrid information…")
timegrid = s.getTimegridUnits()
meta["timegrid"] = []
for tg in timegrid:
    meta["timegrid"].insert(tg.day, tg.to_json())

box_print("║   ║", "Adding last update times…")
last_update = s.getLatestImportTime()
meta["lastUpdated"] = last_update.strftime("%d.%m.%Y %H:%M:%S")
meta["lastUpdatedISO8601"] = last_update.strftime("%Y-%m-%d %H:%M:%S")

lastGeneratedDate = datetime.now()
meta["lastGenerated"] = lastGeneratedDate.strftime("%d.%m.%Y %H:%M:%S")
meta["lastGeneratedISO8601"] = lastGeneratedDate.strftime("%Y-%m-%d %H:%M:%S")

box_print("║   ║", "Writing meta.json…")
with open(os.path.join(plan_dir, "meta.json"), mode="w", encoding="utf-8") as meta_file:
    meta_file.write(json.dumps(meta, ensure_ascii = False, sort_keys = True, indent = 2))
    box_print("║   ║", "Done.")

#####
# Part where we create timetable files for the web interface
#####

box_print("╠═╣", "Timetable JSON files".upper(), "center")

week3_fri = get_other_weekday(weekday_index = 4, week_index = 2) # Get the last school day of the week after next

# Clamp start and end dates. If one of these dates is not within the schoolyear start and end dates, the API will return an error
clamped_start_date = max(current_schoolyear.start_date, week1_mon)
clamped_end_date = min(current_schoolyear.end_date, week3_fri)

box_print("║   ║", "Requesting substitution data…")
substitutions = s.getSubstitutions(start_date = clamped_start_date.untis_date, end_date = clamped_end_date.untis_date)

for kl in classes:
    box_print("║   ║", "Requesting timetables for {0}…".format(kl))
    
    timetable = s.getTimetableCustom(kl.id, PyUntisElementType.CLASS, 
        start_date = clamped_start_date.untis_date, end_date = clamped_end_date.untis_date,
        showInfo = True, showSubstText = True, showLsText = True, showLsNumber = True, showStudentgroup = True)
        
    timetable_days = [PyUntisDate(d) for d in daterange(clamped_start_date.date, clamped_end_date.date) if d.weekday() < 5]
    
    timetable_json = {}
    timetable_json["weeks"] = [[] for x in range(3)]
    for date in timetable_days:
        day_json = {}
        
        date_week = math.floor(timetable_days.index(date) / 5) # zero-based week index
        
        day_lessons = sorted([t for t in timetable if t.date == date], key=lambda l: l.start_time)
        if len(day_lessons) == 0:
            continue # skip days without any lessons
        
        date_timeunits = timegrid[date.date.weekday()]
        
        last_start_time = 0
        for lesson in day_lessons:
            lesson_json = lesson.to_json()
            
            # note for later: test.sort(function(a, b) { return a.localeCompare(b);})
            if last_start_time != lesson.start_time.untis_time:
                # This is a new time slot, create new lesson
                day_json[lesson.start_time.untis_time] = [lesson_json]
            else:
                # This time slot already exists, append lesson
                day_json[lesson.start_time.untis_time].append(lesson_json)
            
            last_start_time = lesson.start_time.untis_time

        timetable_json["weeks"][date_week].append(day_json)
    
    class_substitutions = [subst for subst in substitutions if kl in subst.classes]
    timetable_json["substitutions"] = []
    for subst in class_substitutions:
        subst_json = subst.to_json()
        if subst_json:
            timetable_json["substitutions"].append(subst_json)
        
    timetable_dumped = json.dumps(timetable_json, ensure_ascii=False)
    plan_file_name = "{0}.json".format(kl.id)
    with open(os.path.join(plan_dir, plan_file_name), mode="w", encoding="utf-8") as plan_file:
        plan_file.write(timetable_dumped)
        box_print("║   ║", "{0} written.".format(plan_file_name), "right")
        
box_print("╠╦═╦╣")
box_print("║║ ║║", "Logging out…", "center")

s.logout()

tock = datetime.now()
diff = tock - tick

box_print("║║ ║║", "Finished in {0}".format(diff), "center")
box_print("╚╩═╩╝")