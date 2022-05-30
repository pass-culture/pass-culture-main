
import pcapi.scheduled_tasks.commands
from pcapi.infratest.components import crons
import yaml
from pcapi.infratest.components.crons import Cron

def format_cron(cron: Cron):
    return {
        "command": cron.command,
        "schedule": cron.schedule,
        "profile": cron.profile.value,
        "backoffLimit": cron.backoff_limit,
    }

if __name__ == "__main__":
    print(yaml.dump([format_cron(cron) for cron in crons.crons_list]))
