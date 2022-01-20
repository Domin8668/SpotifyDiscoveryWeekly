import base64


spotify_user_id = "domiins"
discover_weekly_id = "37i9dQZEVXcP6X8abxWKSF"

refresh_token = "AQBtJO9gXoZEew79eoecggYcrSabg4igWaF7VRDGVbF2YaK3piATbsvfDlS9Jf6imOAP0APrwA6OIeSwxypmOlGpFaYdZpD2wf_4hlpJRtM9zU4Zl0X-9rKyavDpLR7E5u4"
redirect_uri = "https%3A%2F%2Fsave.dw"

client_secret = '3d2a3a5a64884371b1b28207a0130017'
client_id = '7887fe78ed5d44e9bb95a7a901246b38'

client_creds = f'{client_id}:{client_secret}'
client_creds_base64 = base64.b64encode(client_creds.encode()).decode()
print(client_creds_base64)