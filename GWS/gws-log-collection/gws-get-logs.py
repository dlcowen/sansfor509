from __future__ import print_function
from googleapiclient.discovery import build
import json
from google.oauth2 import service_account

class Google(object):
    """
    Class for connecting to API and retreiving longs
    """

    def __init__(self):
        self.SERVICE_ACCOUNT_FILE = config['creds_path']
        self.delegated_creds = config['delegated_creds']
        self.output_path = config['output_path']
        self.service = self.google_session()

    def google_session(self):
        """
        Establish connection to Google Wrospace.
        """
        
        SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly', 'https://www.googleapis.com/auth/apps.alerts']
        creds = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        delegated_credentials = creds.with_subject(self.delegated_creds)

        service = build('admin', 'reports_v1', credentials=delegated_credentials)

        return service

    def get_login_activity(self):

        # Call the Admin SDK Reports API
        results = self.service.activities().list(
            userKey='all', applicationName='login').execute()
        activities = results.get('items', [])
        for entry in activities:
            json_formatted_str = json.dumps(entry)
            with open(f"{self.output_path}/login_logs.json", 'a') as output:
                output.write(f"{json_formatted_str}\n")

    def get_drive_activity(self):

        # Call the Admin SDK Reports API
        results = self.service.activities().list(
            userKey='all', applicationName='drive').execute()
        activities = results.get('items', [])
        for entry in activities:
            json_formatted_str = json.dumps(entry)
            with open(f"{self.output_path}/drive_logs.json", 'a') as output:
                output.write(f"{json_formatted_str}\n")

    def get_admin_activity(self):

        # Call the Admin SDK Reports API
        results = self.service.activities().list(
            userKey='all', applicationName='admin').execute()
        activities = results.get('items', [])
        for entry in activities:
            json_formatted_str = json.dumps(entry)
            with open(f"{self.output_path}/admin_logs.json", 'a') as output:
                output.write(f"{json_formatted_str}\n")

    def get_user_activity(self):

        # Call the Admin SDK Reports API
        results = self.service.activities().list(
            userKey='all', applicationName='user_accounts').execute()
        activities = results.get('items', [])
        for entry in activities:
            json_formatted_str = json.dumps(entry)
            with open(f"{self.output_path}/user_logs.json", 'a') as output:
                output.write(f"{json_formatted_str}\n")
    
    def get_chat_activity(self):

        # Call the Admin SDK Reports API
        results = self.service.activities().list(
            userKey='all', applicationName='chat').execute()
        activities = results.get('items', [])
        for entry in activities:
            json_formatted_str = json.dumps(entry)
            with open(f"{self.output_path}/chat_logs.json", 'a') as output:
                output.write(f"{json_formatted_str}\n")
    
    def get_calendar_activity(self):

        # Call the Admin SDK Reports API
        results = self.service.activities().list(
            userKey='all', applicationName='calendar').execute()
        activities = results.get('items', [])
        for entry in activities:
            json_formatted_str = json.dumps(entry)
            with open(f"{self.output_path}/calendar_logs.json", 'a') as output:
                output.write(f"{json_formatted_str}\n")
    
    def get_token_activity(self):

        # Call the Admin SDK Reports API
        results = self.service.activities().list(
            userKey='all', applicationName='token').execute()
        activities = results.get('items', [])
        for entry in activities:
            json_formatted_str = json.dumps(entry)
            with open(f"{self.output_path}/token_logs.json", 'a') as output:
                output.write(f"{json_formatted_str}\n")
            

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

google = Google()
google.get_login_activity()
google.get_drive_activity()
google.get_admin_activity()
google.get_user_activity()
google.get_chat_activity()
google.get_calendar_activity()