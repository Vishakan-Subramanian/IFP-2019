#Python script to write the sensor data to a Google Sheet

#Sheets API
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint


def write_to_sheets(new_data):
    """Pass a new data row as a list to write to Google Sheets"""

    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    #Credentials to authorize the Google Sheets/Drive API, using credentials.json file
    creds = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/Desktop/Code/credentials.json', scope)
    client = gspread.authorize(creds)

    #Open the required sheet
    sheet = client.open('Sensor Data').sheet1

    #Add the newly obtained data to the sheet in the following format
    #new_data = ["time", "mq5", "mq9", "mq135", "humidity", "temp", "pressure", "dust"]

    sheet.append_row(new_data)
