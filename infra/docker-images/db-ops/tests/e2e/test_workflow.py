import os
import string
import subprocess
import random
from datetime import date
from time import sleep
import urllib.request
import base64

from googleapiclient import discovery

class TestE2E:
    project = "passculture-metier-ehp"
    instance_name = "test-db-ops-%s-%s" % (date.today().strftime("%Y-%m-%d"), (''.join(random.choice(string.ascii_letters) for i in range(6))).lower())
    instance_region = "europe-west1"
    secret_env_vars_dict = {}

    @classmethod
    def setup_class(cls):
        secretmanager_service = discovery.build('secretmanager', 'v1')

        secret_env_vars = [
            "ADMINISTRATION_EMAIL_ADDRESS",
            "ALGOLIA_API_KEY",
            "ALGOLIA_APPLICATION_ID",
            "ALLOCINE_API_KEY",
            "CLOUD_TASK_BEARER_TOKEN",
            "DEMARCHES_SIMPLIFIEES_TOKEN",
            "DEMARCHES_SIMPLIFIEES_WEBHOOK_TOKEN",
            "DEV_EMAIL_ADDRESS",
            "EXPORT_TOKEN",
            "FLASK_SECRET",
            "FTP_TITELIVE_PWD",
            "FTP_TITELIVE_URI",
            "FTP_TITELIVE_USER",
            "JOUVE_API_DOMAIN",
            "JOUVE_PASSWORD",
            "JOUVE_USERNAME",
            "JOUVE_VAULT_GUID",
            "JWT_SECRET_KEY",
            "MAILJET_API_KEY",
            "MAILJET_API_SECRET",
            "OVH_BUCKET_NAME",
            "OVH_PASSWORD",
            "OVH_REGION_NAME",
            "OVH_TENANT_NAME",
            "OVH_USER",
            "PASS_CULTURE_BIC",
            "PASS_CULTURE_IBAN",
            "PASS_CULTURE_REMITTANCE_CODE",
            "PAYMENTS_DETAILS_RECIPIENTS",
            "PAYMENTS_REPORT_RECIPIENTS",
            "PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN",
            "RECAPTCHA_SECRET",
            "SENDINBLUE_API_KEY",
            "SENTRY_DSN",
            "SUPPORT_EMAIL_ADDRESS",
            "TRANSACTIONS_RECIPIENTS",
            "WALLET_BALANCES_RECIPIENTS"
        ]

        for secret_env_var in secret_env_vars:
            value = secretmanager_service.projects().secrets().versions().access(
                name="projects/passculture-metier-ehp/secrets/pcapi-staging_%s/versions/latest" % secret_env_var.lower()
            ).execute()["payload"]["data"]
            cls.secret_env_vars_dict.update({secret_env_var: base64.b64decode(value).decode("utf8")})


        external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

        sqladmin_service = discovery.build('sqladmin', 'v1beta4')
        sqladmin_instance_service = sqladmin_service.instances()
        sqladmin_operations_service = sqladmin_service.operations()

        operation = sqladmin_instance_service.insert(
            project=cls.project,
            body={
                "databaseVersion": "POSTGRES_12",
                "name": cls.instance_name,
                "region": cls.instance_region,
                "settings": {
                    "tier": "db-custom-4-15360",
                    "ipConfiguration": {
                        "authorizedNetworks": [{ "value": external_ip }]
                    }
                }
            }
        ).execute()

        while sqladmin_operations_service.get(
            project=cls.project,
            operation=operation["name"]
        ).execute()["status"] != "DONE" :
            print("Operation %s still pending, sleeping %ds..." % (operation["name"], 60))
            sleep(60)

    def test_staging_workflow(self):
        status = subprocess.run(
            "python3 /scripts/staging.py",
            shell=True,
            env=os.environ | self.secret_env_vars_dict | {
                "PRODUCTION_INSTANCE_NAME": "pcapi-production-9fb2eb30",
                "STAGING_INSTANCE_NAME": self.instance_name,
                "STAGING_USER_PASSWORD": "testpassword123",
                "REDIS_URL": "redis://redis/",
                "REINDEX_OFFERS_ENDING_PAGE": "0",
                "REINDEX_OFFERS_LIMIT": "0",
                "REINDEX_OFFERS_CLEAR_OFFERS": "false"
            },
            cwd="/usr/src/app"
        )

        assert status.returncode == 0;

    @classmethod
    def teardown_class(cls):
        service = discovery.build('sqladmin', 'v1beta4')
        sqladmin_instance_service = service.instances()
        sqladmin_operations_service = service.operations()

        operation = sqladmin_instance_service.delete(
            project=cls.project,
            instance=cls.instance_name
        ).execute()

        while sqladmin_operations_service.get(
            project=cls.project,
            operation=operation["name"]
        ).execute()["status"] != "DONE" :
            print("Operation %s still pending, sleeping %ds..." % (operation["name"], 60))
            sleep(60)

        return operation