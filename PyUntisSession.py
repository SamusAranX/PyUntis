#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import json # debug

from urllib.parse import urlencode
from datetime import datetime
from PyUntisClasses import *
try:
	import requests
except ImportError:
	print("PyUntis requires Requests. You'll need it if you want to use PyUntis.")
	raise

class PyUntisSession:
	SCHOOLQUERY_URL = "https://query.webuntis.com/schoolquery?m=searchSchool&v=i2.5.2"
	JSON_API_FORMAT = "https://{0}/WebUntis/jsonrpc.do{1}"
	HTML_API_FORMAT = "https://{0}/WebUntis/Timetable.do"
	
# 	USER_AGENT = "PyUntis 3.0"
	USER_AGENT = "Untis/2.5.2 (at.grupet.mobile.um; build:1; iOS 13.0.0) Alamofire/4.8.1"
	
	def __init__(self):
		self.session = requests.Session()
		self.session.headers = { "User-Agent": self.USER_AGENT, "Content-Type": "application/json;charset=UTF-8", "Cache-Control": "no-cache" }
		
		self.servername = ""
		self.requestID = 0
		
	def _build_payload(self, method, shitty_untis_api_hack=False, **params):
		self.requestID += 1
		
		params = { k:v for k,v in params.items() if v is not None }
		
		payload = { "method": method, "id": "UntisMobileiOS", "jsonrpc": "2.0" }
		if params:
			payload["params"] = [params] if shitty_untis_api_hack else params
		return payload
		
	def searchSchools(self, searchString):
		payload = self._build_payload("searchSchool", shitty_untis_api_hack=False, search = searchString)

		print(payload)
		
		r = self.session.post(self.SCHOOLQUERY_URL, json = payload)
		response = r.json()
		
		if "error" in response:
			raise PyUntisError(response["error"])
			
		schools = response["result"]["schools"]
		return [PyUntisSchool.from_json(s) for s in schools]
			
	def _post(self, payload, **url_params):
		json_api_url = self.JSON_API_FORMAT.format(self.servername, "?" + urlencode(url_params) if url_params else "")

		# print(json_api_url, payload)
		
		r = self.session.post(json_api_url, json = payload)
		response = r.json()
		
		if "error" in response:
			return []
			# raise PyUntisError(response["error"])
		
		if "result" in response:
			return response["result"]
		else:
			print(response)
		
	def authenticate(self, school, username, password=None):
		self.servername = school.server
		payload = self._build_payload("authenticate", user=username, password=password, client=self.USER_AGENT)
		response = self._post(payload, school = school.login_name)
		
		return PyUntisAuthResult(response)
		
	def logout(self):
		payload = self._build_payload("logout")
		self._post(payload)
		# This is a fire-and-forget method without any output
		
	def getTeachers(self):
		payload = self._build_payload("getTeachers")
		response = self._post(payload)
		
		# return list of PyUntisTeacher objects (untested)
		return [PyUntisTeacher(t) for t in response]
		
	def getStudents(self):
		payload = self._build_payload("getStudents")
		response = self._post(payload)
		
		# return list of PyUntisStudent objects (untested)
		return [PyUntisStudent(s) for s in response]
		
	def getKlassen(self, schoolyear_id=None):
		payload = self._build_payload("getKlassen", schoolyearId = schoolyear_id)
		response = self._post(payload)
		
		return [PyUntisClass(kl) for kl in response]
		
	def getSubjects(self):
		payload = self._build_payload("getKlassen")
		response = self._post(payload)
		
		return [PyUntisSubject(sb) for sb in response]
		
	def getRooms(self):
		payload = self._build_payload("getRooms")
		response = self._post(payload)
		
		return [PyUntisRoom(r) for r in response]
		
	def getDepartments(self):
		payload = self._build_payload("getDepartments")
		response = self._post(payload)
		
		return [PyUntisDepartment(d) for d in response]
		
	def getHolidays(self):
		payload = self._build_payload("getHolidays")
		response = self._post(payload)
		
		return [PyUntisHoliday(h) for h in response]
		
	def getTimegridUnits(self):
		payload = self._build_payload("getTimegridUnits")
		response = self._post(payload)
		
		# return response
		return [PyUntisDayGrid(tu) for tu in response]
	
	def getStatusData(self):
		payload = self._build_payload("getStatusData")
		response = self._post(payload)
		
		return PyUntisStatusData(response)
		
	def getCurrentSchoolyear(self):
		payload = self._build_payload("getCurrentSchoolyear")
		response = self._post(payload)
		
		return PyUntisSchoolyear(response)
		
	def getSchoolyears(self):
		payload = self._build_payload("getSchoolyears")
		response = self._post(payload)
		
		return [PyUntisSchoolyear(sy) for sy in response]
		
	def getTimetable(self, id, type, start_date=None, end_date=None):
		payload = self._build_payload("getTimetable", id=id, type=type, startDate=start_date.untis_date, endDate=end_date.untis_date)
		response = self._post(payload)
		
		return [PyUntisTimetableEntry(t) for t in response]
		
	def getTimetableCustom(self, id, type, start_date=None, end_date=None, keyType="id", **params):
		fields = params["fields"] if "fields" in params else ["id", "name", "longname"]
		element = {"id": id, "type": type, "keyType": keyType}
		params = { k:v for k,v in params.items() if v is not None }
		options = {
			"element": element, "startDate": start_date, "endDate": end_date,
			"klasseFields": fields, "roomFields": fields, "subjectFields": fields, "teacherFields": fields,
			**params
		}
		payload = self._build_payload("getTimetable", options=options)        
		response = self._post(payload)
		
		return [PyUntisTimetableEntry(t) for t in response]
		
	def getLatestImportTime(self):
		payload = self._build_payload("getLatestImportTime")
		response = self._post(payload)
		
		return datetime.fromtimestamp(response / 1000.0)
		
	def getSubstitutions(self, start_date=None, end_date=None, department_id=0):
		payload = self._build_payload("getSubstitutions", startDate = start_date, endDate=end_date, departmentId=department_id)
		response = self._post(payload)
		
		return [PyUntisSubstitution(subst) for subst in response]
		
	def getExams(self, exam_type_id, start_date, end_date):
		payload = self._build_payload("getExams", examTypeId=exam_type_id, startDate=start_date, endDate=end_date)
		response = self._post(payload)
		
		return response
		
	def getExamTypes(self):
		payload = self._build_payload("getExamTypes")
		response = self._post(payload)
		
		return response