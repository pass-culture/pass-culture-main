import datetime
import statistics

import pytz


def get_eta(end, current, elapsed_per_batch, batch_size: int):  # type: ignore [no-untyped-def]
    left_to_do = end - current
    eta = left_to_do / batch_size * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta
