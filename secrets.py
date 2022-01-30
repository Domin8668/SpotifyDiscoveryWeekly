import base64


class Data:
    spotify_user_id = ""
    discover_weekly_id = ""

    refresh_token = ""
    redirect_uri = ""

    __client_secret = ''
    __client_id = ''
    client_creds_base64 = base64.b64encode(f'{__client_id}:{__client_secret}'.encode()).decode()
