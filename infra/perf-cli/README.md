## PCAPI cli test


click doc: https://click.palletsprojects.com/en/stable/

Create venv
    cd infra/perf-cli
    python3 -m venv venv

Activate venv

    source venv/bin/activate

Install requirements

    pip install -r requirements.txt


Export NETSKOPE Certificate

    export REQUESTS_CA_BUNDLE="/Library/Application Support/Netskope/STAgent/data/nscacert.pem"

Export pre requisite vars

    export PCAPI_BASE_URL="https://backend.testing.passculture.team"
    export ACCESS_TOKEN="<ACCESS-TOKEN-HERE>"


Cli usage

    python main.py --help

Usage with number of request and concurrent

    python main.py offer -n 100 -c 20


https://app.testing.passculture.team/offre/2748
payload = {offer_ids: [395823444, 391407249, 385589055]}

https://backoffice.testing.passculture.team/admin/feature-flipping
ENABLE_NATIVE_APP_RECAPTCHA