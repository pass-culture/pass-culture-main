from pcapi import settings
from pcapi.utils import requests


DISCORD_BOT_TOKEN = settings.DISCORD_BOT_TOKEN
DISCORD_GUILD_ID = "1202586082508808232"
DISCORD_CLIENT_ID = "1261948740915433574"
DISCORD_CLIENT_SECRET = settings.DISCORD_CLIENT_SECRET
DISCORD_CALLBACK_URI = f"{settings.API_URL}/auth/discord/callback"
DISCORD_REDIRECT_SUCCESS = f"{settings.API_URL}/auth/discord/success"
DISCORD_FULL_REDIRECT_URI = (
    f"https://discord.com/api/oauth2/authorize"
    f"?client_id={DISCORD_CLIENT_ID}"
    f"&redirect_uri={DISCORD_CALLBACK_URI}"
    f"&response_type=code"
    f"&scope=identify%20guilds.join"
)
DISCORD_HOME_URI = f"https://discord.com/channels/{DISCORD_GUILD_ID}/@home"


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


def add_to_server(access_token: str) -> None:
    """
    Adds the user to the pass culture discord server
    Our server is identified by the DISCORD_GUILD_ID
    """
    user_response = requests.get(
        "https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}
    )
    user_response.raise_for_status()

    user_id = user_response.json()["id"]
    data = {"access_token": access_token}
    url = f"https://discord.com/api/guilds/{DISCORD_GUILD_ID}/members/{user_id}"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}", "Content-Type": "application/json"}

    requests.put(url, json=data, headers=headers)
