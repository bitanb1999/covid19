import requests
import re
import os.path
from os import path
import bs4
from bs4 import BeautifulSoup
import couchdb
from datetime import datetime
import hashlib
import json

# I scripted this in urgency, So code quality or the logic isn't great.
# This is mostly a hack. 

pushover_api_token =str(os.environ.get("pushover_api_token"))
pushover_user_key = str(os.environ.get("pushover_user_key"))
pushover_url = "https://api.pushover.net/1/messages.json"
covid_db_full_url = str(os.environ.get("covid_db_full_url"))
archive_folder_path = str(os.environ.get("archive_folder_path")) 

states = {
	"Andhra Pradesh": "AP",
	"Arunachal Pradesh": "AR",
	"Assam": "AS",
	"Bihar": "BR",
	"Bihar****": "BR",
	"Chattisgarh": "CT",
	"Chhattisgarh": "CT",
	"Goa": "GA",
	"Gujarat": "GJ",
	"Haryana": "HR",
	"Himachal Pradesh": "HP",
	"Jharkhand": "JH",
	"Jharkhand#": "JH",
	"Karnataka": "KA",
	"Kerala": "KL",
	"Madhya Pradesh": "MP",
	"Madhya Pradesh#": "MP",
	"Madhya Pradesh***": "MP",
	"Maharashtra": "MH",
	"Maharashtra***": "MH",
	"Manipur": "MN",
	"Meghalaya": "ML",
	"Mizoram": "MZ",
	"Nagaland": "NL",
	"Nagaland#": "NL",
	"Odisha": "OR",
	"Punjab": "PB",
	"Punjab***": "PB",
	"Rajasthan": "RJ",
	"Sikkim": "SK",
	"Tamil Nadu": "TN",
	"Telengana": "TG",
	"Telangana***": "TG",
	"Telengana***": "TG",
	"Tripura": "TR",
	"Uttarakhand": "UT",
	"Uttar Pradesh": "UP",
	"West Bengal": "WB",
	"Andaman and Nicobar Islands": "AN",
	"Chandigarh": "CH",
	"Chandigarh***": "CH",
	"Dadra and Nagar Haveli": "DN",
	"Dadar Nagar Haveli": "DN",
	"Daman and Diu": "DD",
	"Daman & Diu": "DD",
	"Delhi": "DL",
	"Jammu and Kashmir": "JK",
	"Ladakh": "LA",
	"Lakshadweep": "LD",
	"Pondicherry": "PY",
	"Puducherry": "PY",
	"Dadra and Nagar Haveli and Daman and Diu": "DN_DD",
	"Telangana": "TG",
}

def getCurrentDataTimeAsString():
	now = datetime.now()
	print("now =", now)
	#current_date_time = now.strftime("%d-%m-%YT%H-%M-%S")
	datepart =  now.strftime("%Y-%m-%d")
	return f"{datepart}T08:00:00.00+05:30"


def getDataJSON():	
	url = f"https://www.mohfw.gov.in/data/datanew.json?{getCurrentDataTimeAsString()}"
	r = requests.get(url)
	txt = ""
	if r.status_code == 200:
		return r.text

def checkIfThisFileExists(partial_file_name):
	for filename in os.listdir(archive_folder_path.format("data_json")):
		if filename.endswith(partial_file_name):
			just_file_name = (filename.split("/"))[0]
			#12-04-2020T22-49-55_md5_6eb1457605b8dada8ffd89b8fbb6ffa0.json
			just_file_name = just_file_name.replace(partial_file_name, "")
			just_file_names = just_file_name.split("T")
			day_part = just_file_names[1]
			time_part = just_file_names[0]
			time_part = time_part.replace("-",":")
			report_time = f"{day_part}T{time_part}:00.00+05:30"
			return True, filename, report_time
	return False, "", ""

def getDataJSONFileName(partial_file_name):
	current_date_time = getCurrentDataTimeAsString()
	return current_date_time+partial_file_name


def load_data(load, current_date_time):
	couchdb_db_name = "covid19"
	couch = couchdb.Server(covid_db_full_url)
	database = couch[couchdb_db_name]
	message = ""
	json_data = json.loads(load)
	for state_data in json_data:
		print("---------------------")
		print(state_data)
		print("---------------------")
		state_name = state_data["state_name"]
		if state_name == "":
			continue

		state_code = states[state_name]
		state_code = state_code.lower()

		_id = f"{current_date_time}|{state_code}"

		data = {
			"_id": _id,
			"state": state_code,
			"report_time": current_date_time,
			"cured": int(state_data["new_cured"]),
			"death": int(state_data["new_death"]),
			"confirmed": int(state_data["new_positive"]),
			"source": "mohfw",
			"type": "cases",
		}
		try:
			if database[_id]:
				print("***** EXISTS *****")
				#print(counter)
				print(data)
				message = message + " \n EXISTS " +str(_id) +" \n"
		except couchdb.http.ResourceNotFound:
				print("##### ADDING #####")
				#print(counter)
				message = message + " \n ADDING " +str(_id) +" \n"
				database.save(data)	
				print(data)



def scrape_data_now():
	load = True
	current_date_time = getCurrentDataTimeAsString()
	data = getDataJSON()
	h = hashlib.md5(data.encode()).hexdigest()
	print("hash:",h)
	partial_file_name = "_md5_{0}.json".format(h)
	print("partial_file_name:",partial_file_name)

	exists, filename, report_time = checkIfThisFileExists(partial_file_name)

	if exists:
		print("Exists:", filename)
	else:
		json_full_file_name = archive_folder_path.format("data_json")+"/"+getDataJSONFileName(partial_file_name)
		print("creating:", json_full_file_name)
		f = open(json_full_file_name, "a")
		f.write(data)
		load_data(data, current_date_time)
			

def load_file_now(file_name, file_date_time):
	x = json_full_file_name = archive_folder_path.format("data_json")+"/"+file_name
	with open(x, 'r') as file:
		file_data = file.read()
		load_data(file_data, file_date_time)

# def reload_a_day_backup(file_name):
# 	couchdb_db_name = "covid19"
# 	couch = couchdb.Server(covid_db_full_url)
# 	database = couch[couchdb_db_name]
# 	message = ""

# 	x = json_full_file_name = archive_folder_path.format("data_json")+"/"+file_name
# 	json_data = []
# 	with open(x, 'r') as f:
# 		for line in f:
# 			print(line[:-1])
# 			json_data.append(json.loads(line[:-2]))
# 			#break
# 	for data_doc in json_data:
# 		data = data_doc["value"]
# 		print(data)
# 		_id = data["_id"]
# 		del data["_rev"]
# 		try:
# 			if database[_id]:
# 				print("***** EXISTS *****")
# 				#print(counter)
# 				print(data)
# 				message = message + " \n EXISTS " +str(_id) +" \n"
# 		except couchdb.http.ResourceNotFound:
# 				print("##### ADDING #####")
# 				#print(counter)
# 				message = message + " \n ADDING " +str(_id) +" \n"
# 				database.save(data)	
# 				print(data)





if __name__ == "__main__":
	#load_file_now("2021-07-09T08:00:00.00+05:30_md5_371ac6059334fcf03ec27815a73da119.json", "2021-07-09T08:00:00.00+05:30")
	scrape_data_now()
	#reload_a_day_backup("2020-07-28.json")
