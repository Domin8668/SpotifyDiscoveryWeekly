from secrets import Data
from datetime import date
from refresh import Refresh
import requests
import json


class SaveSongs:
    def __init__(self):
        self.user_id = Data.spotify_user_id
        self.spotify_token = "AQBtJO9gXoZEew79eoecggYcrSabg4igWaF7VRDGVbF2YaK3piATbsvfDlS9Jf6imOAP0APrwA6OIeSwx" \
                             "ypmOlGpFaYdZpD2wf_4hlpJRtM9zU4Zl0X-9rKyavDpLR7E5u4"
        self.discover_weekly_id = Data.discover_weekly_id
        self.tracks = ""
        self.new_playlist_id = ""

    def call_refresh(self):
        print("Refreshing token...")
        # Refreshing the authorization token.
        refresh_caller = Refresh()
        self.spotify_token = refresh_caller.refresh()
        # Finding songs.
        self.find_songs()

    def find_songs(self):

        print("Finding songs in discover weekly...")
        query = f'https://api.spotify.com/v1/playlists/{Data.discover_weekly_id}/tracks'
        headers = {"Content-Type": "application/json",
                   "Authorization": f'Bearer {self.spotify_token}'}
        # Getting the playlist data.
        response = requests.get(query, headers=headers)
        response_json = response.json()
        print(f'{response=}')

        tracks_list = [i["track"]["uri"] for i in response_json["items"]]
        self.tracks = ",".join(tracks_list)
        # print(f'{self.tracks}')

        self.add_to_playlist()

    def add_to_playlist(self):
        print("Adding songs...")
        # Creating a new playlist.
        self.new_playlist_id = self.create_playlist()

        query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(
            self.new_playlist_id, self.tracks)

        response = requests.post(query, headers={"Content-Type": "application/json",
                                                 "Authorization": "Bearer {}".format(self.spotify_token)})

        print(response.json)

    def create_playlist(self):
        # TODO
        print("Trying to create playlist...")
        today = date.today()

        today = today.strftime("%d/%m/%Y")

        query = f"https://api.spotify.com/v1/users/{Data.spotify_user_id}/playlists"

        request_body = json.dumps({
            "name": today + " discover weekly",
            "description": "Discover weekly rescued once again from the brink of destruction "
                           "by your friendly neighbourhood python script", "public": True
        })

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.spotify_token}"
        }
        response = requests.post(query, data=request_body, headers=headers)

        response_json = response.json()

        return response_json["id"]


def main():
    s = SaveSongs()
    s.call_refresh()


if __name__ == "__main__":
    main()
