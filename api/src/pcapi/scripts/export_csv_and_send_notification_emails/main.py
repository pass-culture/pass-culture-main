"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/script-to-export-csv-and-send-notification-emails/api/src/pcapi/scripts/export_csv_and_send_notification_emails/main.py

"""

import argparse

from pcapi.app import app
from pcapi.workers.export_csv_and_send_notification_emails_job import export_csv_and_send_notification_emails


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--batch-label", required=True)
    args = parser.parse_args()

    export_csv_and_send_notification_emails(args.batch_id, args.batch_label)
