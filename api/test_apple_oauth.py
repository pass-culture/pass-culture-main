import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from urllib.parse import parse_qs
from urllib.parse import urlencode

import requests  # noqa: TID251


captured_auth_code = None


class OAuthHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global captured_auth_code  # noqa: PLW0603

        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")
        params = parse_qs(post_data)
        if "code" in params:
            captured_auth_code = params["code"][0]

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Success!</h1><p>POST Received. Code captured in terminal.</p>")

            threading.Thread(target=self.server.shutdown).start()
        else:
            self.send_response(400)
            self.end_headers()


def get_apple_authorization_code(redirect_uri: str, state: str):
    params = {
        "client_id": "app.passculture.web.signin",
        "redirect_uri": redirect_uri,
        "response_mode": "form_post",
        "response_type": "code",
        "scope": "email",
        "state": state,
    }

    auth_url = f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"

    server = HTTPServer(("localhost", 8080), OAuthHandler)

    print("\n" + "=" * 50)
    print("Click the link below to sign in with Apple:")
    print(f"\033[94m{auth_url}\033[0m")
    print("=" * 50)
    print("Waiting for redirect...")

    webbrowser.open(auth_url)

    server.serve_forever()

    print(f"\n[✔] CAPTURED CODE: {captured_auth_code}")
    return captured_auth_code


def get_oauth_state_token(backend_base_url: str) -> str:
    oauth_state_endpoint = f"{backend_base_url}/native/v1/oauth/state"
    response = requests.get(oauth_state_endpoint)
    print(f"status code : {response.status_code}")
    print(f"response: {response.text}")

    token = response.json()["oauthStateToken"]
    return token


def authorize(backend_base_url: str, oauth_state_token: str, authorization_code: str):
    authorize_endpoint = f"{backend_base_url}/native/v1/oauth/apple/authorize"
    payload = {
        "code": authorization_code,
        "state": oauth_state_token,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(authorize_endpoint, json=payload, headers=headers)
        print(f"status code : {response.status_code}")
        print(f"response : {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == "__main__":
    only_test_backend_part = len(sys.argv) > 1 and sys.argv[1] == "b"
    if only_test_backend_part:
        code = sys.argv[2]
        backend_base_url = sys.argv[3]
        state = get_oauth_state_token(backend_base_url)
    else:
        redirect_uri = sys.argv[1]
        state = get_oauth_state_token("http://localhost:5001")
        code = get_apple_authorization_code(redirect_uri, state)
        print("Restart ngrok with backend and copy-paste new url")
        print("❯ ngrok http 5001")
        backend_base_url = input("Backend tunneled url: ")

    authorize(backend_base_url, state, code)
