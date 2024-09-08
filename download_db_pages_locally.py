import requests
import json
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from webpack_video import settings_local as authentication
from lxml import etree
import re
from html import unescape
import xml.etree.ElementTree as ET


qbUsername = authentication.QB_USERNAME
qbPassword = authentication.QB_PASSWORD
qbAppToken = authentication.QB_TOKEN
qbRealmHost = authentication.QB_REALM_HOST
qbHours = authentication.QB_HOURS
qbBaseURL = authentication.QB_BASE_URL
qbApplicationDBID = authentication.QB_APPLICATION_DBID

qbDatabasePagesLibrary = {
    "index.html": 2,
    "index.bundle.js": 3,
}

class DatabaseClient:
    def __init__(self):
        self.qb_dbid = getattr(self, 'qb_dbid', None) 
        self.field_values = {}
        self.username = qbUsername
        self.password = qbPassword
        self.apptoken = qbAppToken
        self.realmhost = qbRealmHost
        self.hours = qbHours
        self.base_url = qbBaseURL
        self.application_dbid = qbApplicationDBID
        self.session = requests.Session()

    def authenticate(self):
        temp_auth = f"{qbBaseURL}/db/main?a=API_Authenticate"
        temp_auth += f"&username={qbUsername}&password={qbPassword}&hours={qbHours}"
        response = requests.post(temp_auth)
        ticket = etree.fromstring(response.content).findtext('ticket')
        return ticket

    def download_all_quickbase_pages(self):
        authentication_ticket = self.authenticate()
        print("this is the ticket", authentication_ticket)
        # Iterate Through Each Page From Dictionary Above
        for page, id_value in qbDatabasePagesLibrary.items():
            print(f"Page: {page}, ID: {id_value}")
            # Download Each Page Individually
            dbPageUrl = f"{qbBaseURL}/db/{qbApplicationDBID}?a=API_GetDBPage&ticket={authentication_ticket}"
            dbPageUrl += f"&pageid={id_value}&apptoken={qbAppToken}"
            qbPageResponse = requests.post(dbPageUrl)
            if qbPageResponse.status_code == 200:
                # Parse the XML content
                root = ET.fromstring(qbPageResponse.text)
                # Find the <pagebody> element
                pagebody_element = root.find('.//pagebody')
                pagebody_content = ''.join(pagebody_element.itertext())
                # Create the folder if it doesn't exist
                folder_name = "local_db_pages"
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                
                # Define the local file name and path
                local_file_name = os.path.join(folder_name, page)
                with open(local_file_name, "w", encoding="utf-8") as file:
                    file.write(pagebody_content)
            else:
                print(f"Request failed with status code: {qbPageResponse.status_code}")

# Example usage
client = DatabaseClient()
client.download_all_quickbase_pages()
