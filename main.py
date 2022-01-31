from secrets import Data
from datetime import date, timedelta
from refresh import Refresh
import requests
import json


class SaveSongs:
    def __init__(self):
        self.user_id = Data.spotify_user_id
        self.spotify_token = "AQBtJO9gXoZEew79eoecggYcrSabg4igWaF7VRDGVbF2YaK3piATbsvfDlS9Jf6imOAP0APrwA6OIeSwx" \
                             "ypmOlGpFaYdZpD2wf_4hlpJRtM9zU4Zl0X-9rKyavDpLR7E5u4"
        self.discover_weekly_id = Data.discover_weekly_id
        self.tracks = ''
        self.new_playlist_id = ''
        self.name = ''

    def start(self):
        print("Refreshing token...")
        # Refreshing the authorization token.
        self.spotify_token = Refresh.refresh()
        # Checking if the playlist already exists.
        self.check_playlist()

    def check_playlist(self):
        print("Checking if the playlist exists...")
        # Creating the name.
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        self.name = f'Discover Weekly {monday.strftime("%d/%m/%Y")}'
        # Getting all the playlist followed by the user.
        query = f'https://api.spotify.com/v1/users/{Data.spotify_user_id}/playlists'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.spotify_token}'
        }
        response = requests.get(query, headers=headers)
        # Checking if the playlist already exists.
        response_json = response.json()
        for playlist in response_json["items"]:
            if playlist["name"] == self.name:
                print("This playlist already exists.")
                return 0
        self.create_playlist()

    def create_playlist(self):
        print("Trying to create playlist...")
        # Creating a new playlist.
        query = f'https://api.spotify.com/v1/users/{Data.spotify_user_id}/playlists'
        request_body = json.dumps({
            "name": self.name,
            "description": "Discover weekly rescued once again from the brink of destruction "
                           "by your friendly neighbourhood python script", "public": True
        })
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.spotify_token}'
        }
        response = requests.post(query, data=request_body, headers=headers)
        response_json = response.json()
        # Getting the playlist id.
        self.new_playlist_id = response_json["id"]
        self.find_songs()

    def find_songs(self):
        # Finding all the songs to add.
        print("Finding songs in discover weekly...")
        query = f'https://api.spotify.com/v1/playlists/{Data.discover_weekly_id}/tracks'
        headers = {"Content-Type": "application/json",
                   "Authorization": f'Bearer {self.spotify_token}'}
        response = requests.get(query, headers=headers)
        response_json = response.json()
        # Get all the songs from Discover Weekly.
        tracks_list = [i["track"]["uri"] for i in response_json["items"]]
        self.tracks = ",".join(tracks_list)
        self.add_to_playlist()

    def add_to_playlist(self):
        # Adding songs to the new playlist.
        print("Adding songs...")
        query = f'https://api.spotify.com/v1/playlists/{self.new_playlist_id}/tracks?uris={self.tracks}'
        headers = {"Content-Type": "application/json",
                   "Authorization": f'Bearer {self.spotify_token}'}
        response = requests.post(query, headers=headers)
        if response.status_code == 201:
            print("Songs were added to the playlist!")
            return 0
        else:
            print(f'There was a {response.status_code} error.')
            return -1


def main():
    s = SaveSongs()
    s.start()


if __name__ == "__main__":
    main()
