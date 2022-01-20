from secrets import client_creds_base64, refresh_token
import requests
import json


class Refresh:
    def __init__(self):
        self.refresh_token = refresh_token
        self.client_creds_base64 = client_creds_base64

    def refresh(self):
        query = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        headers = {
            "Authorization": "Basic " + client_creds_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(query,
                                 data=data,
                                 headers=headers)

        response_json = response.json()
        print(response_json)
        return response_json["access_token"]


a = Refresh()
a.refresh()