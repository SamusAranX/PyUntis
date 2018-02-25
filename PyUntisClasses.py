#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from datetime import datetime
from collections.abc import Sequence
   
class PyUntisError(Exception):
	WEBUNTIS_ERRORS = {
		-7004: "Date out of bounds",
		-8500: "Invalid school name",
		-8509: "Access to substitutions denied",
		-8998: "Worthless error message",
		-32601: "Method not found",
		-32700: "Parse error: No content to map due to end-of-input"
	}
	
	def __init__(self, errorJSON):
		self.error_id = errorJSON["code"]
		self.error_msg = errorJSON["message"]
		if self.error_id in self.WEBUNTIS_ERRORS:
			self.error_msg_friendly = self.WEBUNTIS_ERRORS[self.error_id]
			
	def __str__(self):
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
	ISO8601_FMT = "%Y-%m-%d"
	
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

	def iso8601(self):
		return self.date.strftime(self.ISO8601_FMT)
			
	def make_readable(self):
		return self.date.strftime(self.READABLE_DATE_FMT)
		
	def __eq__(self, date2):
		return self.untis_date == date2.untis_date
		
	def __lt__(self, date2):
		return int(self.untis_date) < int(date2.untis_date)
		
	def __le__(self, date2):
		return int(self.untis_date) <= int(date2.untis_date)
		
	def __gt__(self, date2):
		return int(self.untis_date) > int(date2.untis_date)
		
	def __ge__(self, date2):
		return int(self.untis_date) >= int(date2.untis_date)
		
	def __hash__(self):
		return int(self.untis_date)
			
	def __repr__(self):
		return self.untis_date
		
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
			# this is a dirty workaround for the shitty untis API's behavior
			# times are stored as ints, so 7:55 becomes 755 and so on
			# this also means that 00:00 just becomes 0, defeating all format strings
			# the untis API is bad and their creators should feel bad for not making it good
			if untis_time == 0:
				untis_time = "0000"

			self.untis_time = str(untis_time)
			self.time = datetime.strptime(self.untis_time, self.UNTIS_TIME_FMT)
			
	def make_readable(self):
		return self.time.strftime(self.READABLE_TIME_FMT)
		
	def __eq__(self, time2):
		return self.untis_time == time2.untis_time
		
	def __lt__(self, time2):
		return int(self.untis_time) < int(time2.untis_time)
		
	def __le__(self, time2):
		return int(self.untis_time) <= int(time2.untis_time)
		
	def __gt__(self, time2):
		return int(self.untis_time) > int(time2.untis_time)
		
	def __ge__(self, time2):
		return int(self.untis_time) >= int(time2.untis_time)
		
	def __hash__(self):
		return int(self.untis_time)
			
	def __repr__(self):
		return "{0} (\"{1}\")".format(self.time.strftime(self.READABLE_TIME_FMT), self.untis_time)

class PyUntisSchool:
	def __init__(self, display_name, login_name, address, server):
		self.display_name = display_name
		self.login_name = login_name
		self.address = address
		self.server = server

	@classmethod
	def from_json(cls, school_json):
		s = cls(school_json["displayName"], school_json["loginName"], school_json["address"], school_json["server"])
		return s
		
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
		self.original_id = teacher_json.get("orgid") # only used in substitutions
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
		
	def __eq__(self, class2):
		return self.name == class2.name
		
	def __repr__(self):
		return self.name or self.id
		
class PyUntisSubject:
	def __init__(self, subject_json):
		self.id = subject_json["id"]
		self.name = subject_json.get("name")
		self.long_name = subject_json.get("longName")
		self.active = subject_json.get("active") # optional depending on context
		self.did = subject_json.get("did") # optional
		
	def __eq__(self, subject2):
		return self.name == subject2.name
		
	def __repr__(self):
		return self.name or self.id
		
class PyUntisRoom:
	def __init__(self, room_json):
		self.id = room_json["id"]
		self.name = room_json.get("name")
		
		# both of these are only used in substitutions
		self.original_id = room_json.get("orgid") 
		self.original_name = room_json.get("orgname")
		
		self.long_name = room_json.get("longName")
		self.active = room_json.get("active") # optional depending on context
		self.building = room_json.get("building") # optional depending on context
		self.fore_color = room_json.get("foreColor") # optional
		self.back_color = room_json.get("backColor") # optional
		
	def __eq__(self, room2):
		return self.name == room2.name
		
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
		
	def to_json(self):
		return {
			"name": self.long_name,
			"startDate": self.start_date.make_readable(),
			"endDate": self.end_date.make_readable(),
			"startDateISO8601": self.start_date.date.strftime("%Y-%m-%d"),
			"endDateISO8601": self.end_date.date.strftime("%Y-%m-%d"),
			"startDateUntis": self.start_date.untis_date,
			"endDateUntis": self.end_date.untis_date
		} 
		
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
		
class PyUntisDayGrid(Sequence):
	def __init__(self, daygrid_json):
		self.day = (int(daygrid_json["day"]) - 2) % 7
		self.time_units = [PyUntisTimeUnit(tu) for tu in daygrid_json["timeUnits"]]
		super().__init__()
		
	def __getitem__(self, i):
		return self.time_units[i]
		
	def __len__(self):
		return len(self.time_units)
		
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
		
	def to_json(self):
		return {
			"name": self.name,
			"startDate": self.start_date.make_readable(),
			"endDate": self.end_date.make_readable(),
			"startDateUntis": self.start_date.untis_date,
			"endDateUntis": self.end_date.untis_date
		}
		
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

	@classmethod
	def from_values(cls, stuff):
		return 
		
	def to_json(self):
		entry_json = {}            
		entry_json["subject"] = self.subjects[0].name if self.subjects else "???"
		
		# Remove leading zeros from room names like "022", "001" and so on
		entry_json["room"] = self.rooms[0].name.lstrip("0") if self.rooms else "???"

		entry_json["classes"] = [kl.name for kl in self.classes]
		entry_json["code"] = self.code or ""
		
		entry_json["dateUntis"] = self.date.untis_date
		entry_json["dateReadable"] = self.date.make_readable()
		
		entry_json["startTimeUntis"] = self.start_time.untis_time
		entry_json["startTimeReadable"] = self.start_time.make_readable()
		entry_json["endTimeUntis"] = self.end_time.untis_time
		entry_json["endTimeReadable"] = self.end_time.make_readable()
		
		return entry_json
		
	def __repr__(self):
		return "{date} {start_time} - {end_time}: Subject(s) {subjects} in room(s) {rooms} with class(es) {classes} (Code: {code})".format(
			subjects = [s.name or s.id for s in self.subjects],
			rooms = [r.name or r.id for r in self.rooms],
			classes = [c.name or c.id for c in self.classes],
			date = self.date.make_readable(),
			start_time = self.start_time.make_readable(), 
			end_time = self.end_time.make_readable(), 
			code = self.code
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
		
	def to_json(self):
		if not self.subjects:
			# This substitution object is useless without subject information
			return None
		
		subst_json = {}
		subst_json["type"] = self.type
		
		subst_json["date"] = self.date.untis_date
		subst_json["readableDate"] = self.date.make_readable()
		subst_json["time"] = self.start_time.untis_time
		subst_json["readableTime"] = self.start_time.make_readable()
		
		subst_json["subject"] = self.subjects[0].name
		subst_json["room"] = self.rooms[0].name if self.rooms else ""
		
		if self.teachers:
			te = self.teachers[0]
			subst_teacher = { "newTeacher": te.id }
			if te.original_id:
				subst_teacher["oldTeacher"] = te.original_id
			subst_json["teacher"] = subst_teacher
			
		if self.rooms:
			ro = self.rooms[0]
			subst_room = { "newRoom": ro.name }
			if ro.original_name:
				subst_room["oldRoom"] = ro.original_name
			subst_json["room"] = subst_room
			
		if self.text:
			subst_json["text"] = self.text
		
		return subst_json        
		
	def __repr__(self):
		return "Substitution for class(es) {0} in room(s) {1} on {2}: {3} from {4} to {5} -> {6}".format(
			self.classes, self.rooms, self.date.make_readable(), 
			self.subjects, self.start_time.make_readable(), self.end_time.make_readable(),
			self.reschedule or None
		)
