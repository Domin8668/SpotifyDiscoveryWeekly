from secrets import Data
from datetime import date, timedelta, datetime
from refresh import Refresh
import requests
import json
import os
import sys


class InteractWithSpotify:
    def __init__(self):
        self.user_id: str = Data.spotify_user_id
        self.spotify_token: str = Data.spotify_token
        self.discover_weekly_id: str = Data.playlist_ids['discovery_weekly']
        self.tracks: list = []
        self.new_playlist_id = ''
        self.tracks_object = {'tracks': []}
        self.tracks_object = []

    @staticmethod
    def refresh_token() -> str:
        # Creating a POST request to the api to get a fresh token.
        query = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": Data.refresh_token
        }
        headers = {
            "Authorization": "Basic " + Data.client_creds_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(query, data=data, headers=headers)

        return response.json()["access_token"]

    def get_playlist_snapshot_id(self, spotify_token: str):
        print("Getting the playlist's snapshot id...")
        # Getting the playlist data.
        query_params = 'fields=snapshot_id'
        query = f'https://api.spotify.com/v1/playlists/{Data.playlist_ids["fresh"]}?{query_params}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {spotify_token}'
        }
        response = requests.get(query, headers=headers)
        response_json = response.json()
        return response_json['snapshot_id']

    def does_playlist_exist(self, name: str) -> int:
        print('Checking if the playlist already exists...')
        # Getting all the playlist followed by the user.
        query = f'https://api.spotify.com/v1/users/{Data.spotify_user_id}/playlists'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.spotify_token}'
        }
        response = requests.get(query, headers=headers)
        if response.status_code != 201:
            print(f'There was a {response.status_code} error.')
            return -1
        response_json = response.json()
        # Checking if the playlist already exists.
        for playlist in response_json['items']:
            if playlist['name'] == name:
                print('This playlist already exists.')
                return 0
        return 1

    def create_playlist(self, name: str) -> str:
        if self.does_playlist_exist(name) > 0:
            print('Creating a new playlist...')
            query = f'https://api.spotify.com/v1/users/{Data.spotify_user_id}/playlists'
            request_body = json.dumps({
                'name': name,
                'description': 'Discover weekly copy made by a Python script', 'public': True
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.spotify_token}'
            }
            response = requests.post(query, data=request_body, headers=headers)
            response_json = response.json()
            if response.status_code != 201:
                print(f'There was a {response.status_code} error.')
                return ''
            return response_json['id']

    def get_playlist_tracks(self, playlist_id: str) -> list[str]:
        print('Getting songs from your playlist...')
        query = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {self.spotify_token}'}
        response = requests.get(query, headers=headers)
        response_json = response.json()
        return [item['track']['uri'] for item in response_json['items']]

    def get_playlist_tracks_by_date(self, playlist_id: str, number_of_days: int) -> list[str]:
        print('Finding songs in FRESH...')
        query_params = 'fields=items(added_at,track.uri)'
        query = f'https://api.spotify.com/v1/playlists/{Data.playlist_ids["fresh"]}/tracks?{query_params}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {self.spotify_token}'}
        response = requests.get(query, headers=headers)
        response_json = response.json()
        # Get all the songs from Fresh.
        fresh_tracks = response_json['items']
        # Get relevant dates.
        today = date.today()
        cut_off = today - timedelta(days=14)
        for track in fresh_tracks:
            added_at = datetime.strptime(track['added_at'][:10], '%Y-%m-%d').date()
            if added_at <= cut_off:
                print(f'{added_at}')
                self.tracks.append(track['track']['uri'])
                self.tracks_object.append({'uri': track['track']['uri']})

    def remove_tracks_from_playlist(self, playlist_id: str):
        if self.tracks:
            snapshot_id = self.get_playlist_snapshot_id(playlist_id)
            print('Removing old songs from FRESH...')
            query = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
            request_body = json.dumps({
                'tracks': self.tracks_object,
                'snapshot_id': snapshot_id
            })
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'Bearer {self.spotify_token}'}
            response = requests.delete(query, data=request_body, headers=headers)
            if response.status_code == 200:
                print('Songs were succesfully removed!')
                self.add_tracks_to_playlist(playlist_id)
            else:
                print(f'There was a {response.status_code} error.')
        else:
            print('No song meets the criteria.')

    def add_tracks_to_playlist(self, playlist_id: str, tracks: str) -> int:
        print('Adding songs to the new playlist...')
        query = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={tracks}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {self.spotify_token}'}
        response = requests.post(query, headers=headers)
        if response.status_code == 201:
            print('Songs were added to the playlist!')
            return 1
        else:
            print(f'There was a {response.status_code} error.')
            return -1


class SaveSongs:
    def __init__(self):
        self.user_id: str = Data.spotify_user_id
        self.spotify_token: str = Data.spotify_token
        self.discover_weekly_id: str = Data.playlist_ids['discovery_weekly']
        self.tracks: list = []
        self.new_playlist_id = ''
        self.name = ''
        self.tracks_object = {'tracks': []}
        self.tracks_object = []
        self.snapshot_id = ''

    def start(self):
        print('Refreshing token...')
        # Refreshing the authorization token.
        self.spotify_token = Refresh.refresh()
        # Checking if the playlist already exists.
        # self.check_playlist()
        self.get_fresh()

    def check_playlist(self):
        print('Checking if the playlist exists...')
        # Creating the name.
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        self.name = f'Discover Weekly {monday.strftime("%d/%m/%Y")}'
        # Getting all the playlist followed by the user.
        query = f'https://api.spotify.com/v1/users/{Data.spotify_user_id}/playlists'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.spotify_token}'
        }
        response = requests.get(query, headers=headers)
        # Checking if the playlist already exists.
        response_json = response.json()

        for playlist in response_json['items']:
            if playlist['name'] == self.name:
                print('This playlist already exists.')
                return 0
        self.create_playlist()

    def create_playlist(self):
        print('Trying to create playlist...')
        # Creating a new playlist.
        query = f'https://api.spotify.com/v1/users/{Data.spotify_user_id}/playlists'
        request_body = json.dumps({
            'name': self.name,
            'description': 'Discover weekly rescued once again from the brink of destruction '
                           'by your friendly neighbourhood python script', 'public': True
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.spotify_token}'
        }
        response = requests.post(query, data=request_body, headers=headers)
        response_json = response.json()
        # Getting the playlist id.
        self.new_playlist_id = response_json['id']
        self.find_songs()

    def find_songs(self):
        # Finding all the songs to add.
        print('Finding songs in discover weekly...')
        query = f'https://api.spotify.com/v1/playlists/{Data.playlist_ids["discovery_weekly"]}/tracks'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {self.spotify_token}'}
        response = requests.get(query, headers=headers)
        response_json = response.json()
        # Get all the songs from Discover Weekly.
        self.tracks = [i['track']['uri'] for i in response_json['items']]
        self.add_to_playlist()

    def add_to_playlist(self):
        print('Adding songs to the new playlist...')
        query = f'https://api.spotify.com/v1/playlists/{self.new_playlist_id}/tracks?uris={",".join(self.tracks)}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {self.spotify_token}'}
        response = requests.post(query, headers=headers)
        if response.status_code == 201:
            print('Songs were added to the playlist!')
            return 0
        else:
            print(f'There was a {response.status_code} error.')
            return -1

    def get_fresh(self):
        self.tracks = []
        print('Finding songs in FRESH...')
        query_params = 'fields=items(added_at,track.uri)'
        query = f'https://api.spotify.com/v1/playlists/{Data.playlist_ids["fresh"]}/tracks?{query_params}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {self.spotify_token}'}
        response = requests.get(query, headers=headers)
        response_json = response.json()
        # Get all the songs from Fresh.
        fresh_tracks = response_json['items']
        # Get relevant dates.
        today = date.today()
        cut_off = today - timedelta(days=14)
        for track in fresh_tracks:
            added_at = datetime.strptime(track['added_at'][:10], '%Y-%m-%d').date()
            if added_at <= cut_off:
                print(f'{added_at}')
                self.tracks.append(track['track']['uri'])
                self.tracks_object.append({'uri': track['track']['uri']})
        # print(f'{self.tracks}')
        # print(f'{self.tracks_object}')

        if self.tracks:
            self.get_playlist_snapshot_id()
            print('Removing old songs from FRESH...')
            query = f'https://api.spotify.com/v1/playlists/{Data.playlist_ids["fresh"]}/tracks'
            request_body = json.dumps({
                'tracks': self.tracks_object,
                'snapshot_id': self.snapshot_id
            })
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'Bearer {self.spotify_token}'}
            response = requests.delete(query, data=request_body, headers=headers)
            if response.status_code == 200:
                print('Songs were succesfully removed!')
                self.add_to_fav()
            else:
                print(f'There was a {response.status_code} error.')
        else:
            print('No song meets the criteria.')

    def add_to_fav(self):
        # Adding songs to the new playlist.
        print('Adding songs to FAV...')
        query = f'https://api.spotify.com/v1/playlists/{Data.playlist_ids["fav"]}/tracks?uris={",".join(self.tracks)}'
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {self.spotify_token}'}
        response = requests.post(query, headers=headers)
        if response.status_code == 201:
            print('Songs were added to the playlist!')
            return 0
        else:
            print(f'There was a {response.status_code} error.')
            return -1

    def get_playlist_snapshot_id(self):
        print("Getting the playlist's snapshot id...")
        # Getting the playlist data.
        query_params = 'fields=snapshot_id'
        query = f'https://api.spotify.com/v1/playlists/{Data.playlist_ids["fresh"]}?{query_params}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.spotify_token}'
        }
        response = requests.get(query, headers=headers)
        response_json = response.json()
        self.snapshot_id = response_json['snapshot_id']


def main():
    s = SaveSongs()
    s.start()


if __name__ == '__main__':
    main()
