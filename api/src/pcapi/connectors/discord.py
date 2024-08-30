from pcapi import settings
from pcapi.utils import requests


DISCORD_BOT_TOKEN = settings.DISCORD_BOT_TOKEN
DISCORD_GUILD_ID = "1202586082508808232"
DISCORD_CLIENT_ID = "1261948740915433574"
DISCORD_CLIENT_SECRET = settings.DISCORD_CLIENT_SECRET
DISCORD_CALLBACK_URI = f"{settings.API_URL}/auth/discord/callback"
DISCORD_HOME_URI = f"https://discord.com/channels/{DISCORD_GUILD_ID}/@home"

DISCORD_API_URI = "https://discord.com/api"


def build_discord_redirection_uri(user_id: int) -> str:
    base_uri = f"{DISCORD_API_URI}/oauth2/authorize"
    client_id = DISCORD_CLIENT_ID
    redirect_uri = DISCORD_CALLBACK_URI
    response_type = "code"
    scope = "identify%20guilds.join"

    return f"{base_uri}?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}&scope={scope}&state={user_id}"


def get_user_id(access_token: str) -> str | None:
    url = f"{DISCORD_API_URI}/oauth2/@me"
    user_response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    user_response.raise_for_status()
    try:
        return user_response.json()["user"]["id"]
    except KeyError:
        return None


def retrieve_access_token(code: str) -> str | None:
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_CALLBACK_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    token_response.raise_for_status()

    access_token = token_response.json().get("access_token")
    return access_token


def add_to_server(access_token: str, user_discord_id: str) -> None:
    """
    Adds the user to the pass culture discord server
    Our server is identified by the DISCORD_GUILD_ID
    """
    data = {"access_token": access_token}
    url = f"https://discord.com/api/guilds/{DISCORD_GUILD_ID}/members/{user_discord_id}"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}", "Content-Type": "application/json"}

    response = requests.put(url, json=data, headers=headers)
    response.raise_for_status()
