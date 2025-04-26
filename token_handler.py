import os
import requests
from colorama import Fore, init
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

init(autoreset=True)

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_FILE = "yt_token.json"
CLIENT_SECRET_FILE = "client_secret.json"

def save_token(creds):
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())
    print("[+] Token saved successfully", end=' ')

def load_token():
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        return creds
    return None

def auth_yt():
    print("[+] Authenticating YouTube OAuth...\n")
    creds = load_token()

    if creds and creds.valid:
        print(Fore.GREEN + "ok")
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_token(creds)
            return creds
        except Exception as e:
            print(Fore.RED + f"failed to refresh: {e}")
            return None

    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        save_token(creds)
        print("[+]. New token generated...", end=' ')
        print(Fore.GREEN + "ok")
        return creds
    except Exception as e:
        print(Fore.RED + f"failed to authenticate: {e}")
        return None

def validate_token(creds):
    print("[+] Validating YouTube token...", end=' ')
    try:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",
            headers={"Authorization": f"Bearer {creds.token}"}
        )
        if response.status_code == 200:
            print(Fore.GREEN + "ok")
            return True
        else:
            print(Fore.RED + f"failed ({response.status_code})")
            return False
    except Exception as e:
        print(Fore.RED + f"exception: {e}")
        return False


if __name__ == "__main__":
    creds = auth_yt()
    if creds:
        validate_token(creds)
