#!/usr/bin/env python3
#-*- coding: utf-8 -*-
from datetime import datetime
   
class PyUntisError(Exception):
    WEBUNTIS_ERRORS = {
        -7004: "Date out of bounds",
        -32601: "Method not found"
    }
    
    def __init__(self, errorJSON):
        self.error_id = errorJSON["code"]
        self.error_msg = errorJSON["message"]
        if self.error_id in self.WEBUNTIS_ERRORS:
            self.error_msg_friendly = self.WEBUNTIS_ERRORS[self.error_id]
            
    def __repr__(self):
    	return "{0}: {1}".format(self.error_id, self.error_msg)
    	
class PyUntisElementType:
	C = CLASS = 1
	T = TEACHER = 2
	SB = SUBJECT = 3
	R = ROOM = 4
	ST = STUDENT = 5
    	
class PyUntisDate:
    UNTIS_DATE_FMT = "%Y%m%d"
    READABLE_DATE_FMT = "%d.%m.%Y"
    
    def __init__(self, date=None, untis_date=None):
        if date is None and untis_date is None:
            raise ValueError("You can't create a PyUntisDate object without a date")
            
        if date is not None:
            self.date = date
            # self.untis_date = datetime.strftime(self.UNTIS_DATE_FMT, date)
            self.untis_date = date.strftime(self.UNTIS_DATE_FMT)
        elif untis_date is not None:
            self.untis_date = str(untis_date)
            self.date = datetime.strptime(self.untis_date, self.UNTIS_DATE_FMT)
            
    def make_readable(self):
        return self.date.strftime(self.READABLE_DATE_FMT)
            
    def __repr__(self):
        return "{0} (\"{1}\")".format(self.date.strftime(self.READABLE_DATE_FMT), self.untis_date)
        
class PyUntisTime:
    UNTIS_TIME_FMT = "%H%M"
    READABLE_TIME_FMT = "%H:%M"
    
    def __init__(self, time=None, untis_time=None):
        if time is None and untis_time is None:
            raise ValueError("You can't create a PyUntisTime object without a time")
            
        if time is not None:
            self.time = time
            self.untis_time = datetime.strftime(self.UNTIS_TIME_FMT, time)
        elif untis_time is not None:
            self.untis_time = str(untis_time)
            self.time = datetime.strptime(self.untis_time, self.UNTIS_TIME_FMT)
            
    def make_readable(self):
        return self.time.strftime(self.READABLE_TIME_FMT)
            
    def __repr__(self):
        return "{0} (\"{1}\")".format(self.time.strftime(self.READABLE_TIME_FMT), self.untis_time)

class PyUntisSchool:
    def __init__(self, school_json):
        self.display_name = school_json["displayName"]
        self.login_name = school_json["loginName"]
        self.address = school_json["address"]
        self.server = school_json["server"]
        
    def __repr__(self):
        return "{0} ({1})".format(self.display_name, self.address)
        
class PyUntisAuthResult:
    def __init__(self, auth_json):
        self.session_id = auth_json["sessionId"]
        self.person_type = auth_json["personType"]
        self.person_id = auth_json["personId"]
        
# Beware when using PyUntisTeacher and PyUntisStudent.
# I didn't have any real world data to test those classes with, so they may be unstable.
class PyUntisTeacher:
    def __init__(self, teacher_json):
        self.id = teacher_json["id"]
        self.name = teacher_json.get("name")
        self.fore_name = teacher_json.get("foreName")
        self.long_name = teacher_json.get("longName")
        self.fore_color = teacher_json.get("foreColor")
        self.back_color = teacher_json.get("backColor")
        
    def __repr__(self):
        return self.name

# See above.
class PyUntisStudent:
    def __init__(self, student_json):
        self.id = student_json["id"]
        self.key = student_json.get("key")
        self.name = student_json.get("name")
        self.fore_name = student_json.get("foreName")
        self.long_name = student_json.get("longName")
        self.gender = student_json.get("gender")

class PyUntisClass:
    def __init__(self, class_json):
        self.id = class_json["id"]
        self.name = class_json.get("name")
        self.long_name = class_json.get("longName")
        self.active = class_json.get("active") # optional depending on context
        self.did = class_json.get("did") # optional
        
    def __repr__(self):
        return self.name or self.id
        
class PyUntisSubject:
    def __init__(self, subject_json):
        self.id = subject_json["id"]
        self.name = subject_json.get("name")
        self.long_name = subject_json.get("longName")
        self.active = subject_json.get("active") # optional depending on context
        self.did = subject_json.get("did") # optional
        
    def __repr__(self):
        return self.name or self.id
        
class PyUntisRoom:
    def __init__(self, room_json):
        self.id = room_json["id"]
        self.name = room_json.get("name")
        self.long_name = room_json.get("longName")
        self.active = room_json.get("active") # optional depending on context
        self.building = room_json.get("building") # optional depending on context
        self.fore_color = room_json.get("foreColor") # optional
        self.back_color = room_json.get("backColor") # optional
        
    def __repr__(self):
        return self.name or self.id
        
class PyUntisDepartment:
    def __init__(self, dep_json):
        self.id = dep_json["id"]
        self.name = dep_json["name"]
        self.name = dep_json["longName"]
        
class PyUntisHoliday:
    def __init__(self, holiday_json):
        self.id = holiday_json["id"]
        self.name = holiday_json["name"]
        self.long_name = holiday_json["longName"]
        self.start_date = PyUntisDate(untis_date = holiday_json["startDate"])
        self.end_date = PyUntisDate(untis_date = holiday_json["endDate"])
        
    def __repr__(self):
        return "{0}: {1} - {2}".format(self.long_name, self.start_date.make_readable(), self.end_date.make_readable())
        
class PyUntisTimeUnit:
    def __init__(self, timeunit_json):
        self.name = timeunit_json["name"]
        self.start_time = PyUntisTime(untis_time=timeunit_json["startTime"])
        self.end_time = PyUntisTime(untis_time=timeunit_json["endTime"])
        
    def __repr__(self):
        return "{0}: {1} - {2}".format(self.name, self.start_time.make_readable(), self.end_time.make_readable())
        
    def to_json(self):
        return {
            "name": self.name,
            "startTime": self.start_time.make_readable(),
            "endTime": self.end_time.make_readable(),
            "startTimeUntis": self.start_time.untis_time,
            "endTimeUntis": self.end_time.untis_time,
        }
        
class PyUntisDayGrid:
    def __init__(self, daygrid_json):
        self.day = (int(daygrid_json["day"]) - 2) % 7
        self.time_units = [PyUntisTimeUnit(tu) for tu in daygrid_json["timeUnits"]]
        
    def __repr__(self):
        return "Day {0}: {1}".format(self.day, self.time_units)
        
    def to_json(self):
        return [tu.to_json() for tu in self.time_units]
        
class PyUntisStatusData:
    def __init__(self, status_json):
        self.codes = status_json["codes"]
        self.lesson_types = status_json["lstypes"]
        
class PyUntisSchoolyear:
    def __init__(self, year_json):
        self.id = year_json["id"]
        self.name = year_json["name"]
        self.start_date = PyUntisDate(untis_date = year_json["startDate"])
        self.end_date = PyUntisDate(untis_date = year_json["endDate"])
        
    def __repr__(self):
        return "{0}: {1} - {2}".format(self.name, self.start_date, self.end_date)
        
# {'ro', 'code', 'kl', 'su', 'startTime', 'statflags', 'endTime', 'sg', 'lsnumber', 'id', 'substText', 'date'}
class PyUntisTimetableEntry:
    def __init__(self, tt_entry_json):
        self.id = tt_entry_json["id"]
        self.classes = [PyUntisClass(kl) for kl in tt_entry_json["kl"]]
        self.subjects = [PyUntisSubject(su) for su in tt_entry_json["su"]]
        self.rooms = [PyUntisRoom(ro) for ro in tt_entry_json["ro"]]
        self.date = PyUntisDate(untis_date=tt_entry_json["date"])
        self.start_time = PyUntisTime(untis_time=tt_entry_json["startTime"])
        self.end_time = PyUntisTime(untis_time=tt_entry_json["endTime"])
        self.stat_flags = tt_entry_json.get("statflags")
        self.code = tt_entry_json.get("code")
        self.student_group = tt_entry_json.get("sg")
        self.lesson_number = tt_entry_json.get("lsnumber")
        self.subst_text = tt_entry_json.get("substText")
        
    def __repr__(self):
        return "Subject(s) {0} in room(s) {1} with class(es) {2} on {3} from {4} to {5} (Code: {6})".format(
            [s.name or s.id for s in self.subjects],
            [r.name or r.id for r in self.rooms],
            [c.name or c.id for c in self.classes],
            self.date.make_readable(), self.start_time.make_readable(), self.end_time.make_readable(), self.code
        )
        
class PyUntisReschedule:
    def __init__(self, reschedule_json):
        self.date = PyUntisDate(untis_date=reschedule_json["date"])
        self.start_time = PyUntisTime(untis_time=reschedule_json["startTime"])
        self.end_time = PyUntisTime(untis_time=reschedule_json["endTime"])
        
    def __repr__(self):
        return "{0}, {1} - {2}".format(self.date.make_readable(), self.start_time.make_readable(), self.end_time.make_readable())

# {'ro', 'lsid', 'te', 'startTime', 'date', 'reschedule', 'endTime', 'kl', 'type', 'su', 'txt'}
class PyUntisSubstitution:
    def __init__(self, subst_json):
        self.lsid = subst_json["lsid"]
        self.type = subst_json["type"]
        self.date = PyUntisDate(untis_date=subst_json["date"])
        self.start_time = PyUntisTime(untis_time=subst_json["startTime"])
        self.end_time = PyUntisTime(untis_time=subst_json["endTime"])
        
        self.classes = [PyUntisClass(kl) for kl in subst_json["kl"]]
        self.subjects = [PyUntisSubject(su) for su in subst_json["su"]]
        self.rooms = [PyUntisRoom(ro) for ro in subst_json["ro"]]
        self.teachers = [PyUntisTeacher(te) for te in subst_json["te"]]
        
        self.text = subst_json.get("txt")
        
        self.reschedule = PyUntisReschedule(subst_json["reschedule"]) if "reschedule" in subst_json else None
        
    def __repr__(self):
        return "Substitution for class(es) {0} in room(s) {1} on {2}: {3} from {4} to {5} -> {6}".format(
            self.classes, self.rooms, self.date.make_readable(), 
            self.subjects, self.start_time.make_readable(), self.end_time.make_readable(),
            self.reschedule or None
        )