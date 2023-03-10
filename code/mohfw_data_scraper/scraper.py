import requests
import re
import os.path
from os import path
import bs4
from bs4 import BeautifulSoup
import couchdb

# I scripted this in urgency, So code quality or the logic isn't great.
# This is mostly a hack. 


archive_folder_path = str(os.environ.get("archive_folder_path"))
#date_pattern = "as on : \d\d July 2020, \d\d:\d\d "
date_pattern = "as on : \d\d	July 2020, \d\d:\d\d "
month_formatted = "07"


states = {
	"Andhra Pradesh": "AP",
	"Arunachal Pradesh": "AR",
	"Assam": "AS",
	"Bihar": "BR",
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
	"Maharashtra": "MH",
	"Manipur": "MN",
	"Meghalaya": "ML",
	"Mizoram": "MZ",
	"Nagaland": "NL",
	"Nagaland#": "NL",
	"Odisha": "OR",
	"Punjab": "PB",
	"Rajasthan": "RJ",
	"Sikkim": "SK",
	"Tamil Nadu": "TN",
	"Telengana": "TG",
	"Telangana***": "TG",
	"Tripura": "TR",
	"Uttarakhand": "UT",
	"Uttar Pradesh": "UP",
	"West Bengal": "WB",
	"Andaman and Nicobar Islands": "AN",
	"Chandigarh": "CH",
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




def getFileName(t):
	t = t.replace("as on ","")
	t = t.replace(".","-")
	t = t.replace(" ","-")
	t = t.replace(":","-")
	t = f"{t}.html"
	return t

# This is not a great way of doing this. This is just a hack
# I foculd have used standard date formatter!! 
def getFormattedDate(t):
	x = t.replace("as on : ","", 1)
	parts = x.split(", ")
	print(parts)
	date_parts = (parts[0]).split(" ")
	day = date_parts[0]
	if len(day) == 1:
		day = f"0{day}"

		print("day=", day)
	# month = date_parts[1]
	# if len(month) == 1:
	# 	month = "0"+month
	month = month_formatted

	# year = date_parts[2]
	year = "2021"

	time_parts = (parts[1]).split(" ")
	am_pm = time_parts[1]
	hour = ((time_parts[0]).split(":"))[0]

	# if am_pm == "PM":
	# 	hour = str(int(hour)+12)
	if len(hour) == 1:
		hour = f"0{hour}"

	minute = ((time_parts[0]).split(":"))[1]
	if len(minute) == 1:
		minute = f"0{minute}"

	return "2020-{0}-{1}T{2}:{3}:00.00+05:30".format(month, day,hour,minute)

def getContents():
	url = "https://www.mohfw.gov.in/"
	r = requests.get(url)
	txt = ""
	if r.status_code == 200:
		return r.text

def sendMessage(title, message):
	myobj = {
		"user": pushover_user_key,
		"token": pushover_api_token,
		"message": message,
	}
	try:
		x = requests.post(pushover_url, data = myobj)
	except:
		print(pushover_url)
		print("ERROR IN SENDING MESSAGE TO PUSHOVER")

def scrape_now():
	title = "Started"
	message = "started \n"
	couchdb_db_name = "covid19"
	couch = couchdb.Server(covid_db_full_url)
	database = couch[couchdb_db_name]

	txt = getContents()
	#print(txt)

	x = re.findall(date_pattern, txt)
	extracted_date_text = x[0]
	print("before",extracted_date_text)
	extracted_date_text = extracted_date_text.replace("\t", " ")
	print("after",extracted_date_text)

	full_date_text =  getFormattedDate(extracted_date_text)
	#for force run specific file or date
	full_date_text = "2020-11-09T08-00-00-00+05-30"
	full_file_name =  archive_folder_path.format(getFileName(full_date_text))

	print(full_file_name)
	print(full_date_text)
	counter = 1

	title = f"{title}extracted_date_text {str(extracted_date_text)}"
	message = f"{message}full_file_name ={full_file_name}" + " \n"
	message = f"{message}full_date_text ={full_date_text}" + " \n"
	print(force_run)
	if path.exists(full_file_name):
		message += " FILE EXISTS NOTHING TO BE DONE \n"
		print("FILE Exists and nothing to be done")
		if(force_run):
			with open(full_file_name, "r") as f:
				txt = str(f.read())
		else:
			sendMessage(title, message)
			return 0
	else:
		#Backup first
		message += " WRITING THE FILE \n"
		print("Writing to a file")
		f = open(full_file_name, "a")
		f.write(txt)
		message += " WRITING COMPLETE \n"




if __name__ == "__main__":
	scrape_now()
