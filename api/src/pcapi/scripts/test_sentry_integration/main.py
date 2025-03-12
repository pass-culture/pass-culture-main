from pcapi import settings
from pcapi.app import app


app.app_context().push()

if __name__ == "__main__":
    raise RuntimeError(f"Test Damien SaaS Sentry integration. ENV: {settings.ENV}")
