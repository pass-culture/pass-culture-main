import csv
import datetime
import logging
import statistics
import time

import pytz
from sqlalchemy.exc import OperationalError

from pcapi.flask_app import app
from pcapi.models import db


NB_LOGS = 10

logger = logging.getLogger(__name__)

EXTRACT_FOLDER = "/tmp/"

FILE_CSV = EXTRACT_FOLDER + "extract_products_id_titelive_prod.csv"


def _get_eta(end_id: int, current: int, elapsed_per_batch: list, batch_size: int) -> str:
    left_to_do = end_id - current
    if elapsed_per_batch:
        avg_elapsed_time = statistics.mean(elapsed_per_batch)
        total_eta = left_to_do * avg_elapsed_time
        eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=total_eta)
        eta = eta.astimezone(pytz.timezone("Europe/Paris"))
        eta = eta.strftime("%d/%m/%Y %H:%M:%S")
        return eta
    else:
        return "N/A"


def get_products_ids_from_file() -> list[str]:
    products_ids = []
    with open(FILE_CSV, newline="", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

        for row in csv_reader:
            products_ids.append(row[0])

    return products_ids


def divide_chunks(array: list, n: int) -> list:
    for i in range(0, len(array), n):
        yield array[i : i + n]


def _fix_offers(batch_size: int, chunk_start: int) -> None:
    products_ids = get_products_ids_from_file()
    logger.info("[copy_json_data_from_product] nb of products_ids : %d ", len(products_ids))
    logger.info("[copy_json_data_from_product] batch_size : %d", batch_size)

    chunks = divide_chunks(products_ids, batch_size)
    nb_chunks = len(products_ids) / batch_size
    logger.info("[copy_json_data_from_product] nb of chunks : %d ", nb_chunks)

    elapsed_per_batch = []
    # Nombre maximum de tentatives
    max_attempts = 3
    logger.info("[copy_json_data_from_product] max_attempts : %d", max_attempts)
    i = 0
    start_date = datetime.datetime.utcnow()
    logger.info("[copy_json_data_from_product] start %s", start_date)

    # Fixez la date limite à une date spécifique (jour)
    end_date_limit = datetime.datetime(year=2023, month=12, day=31, hour=0, minute=00, second=0)

    last_ids = []
    for ids in chunks:
        if datetime.datetime.utcnow() >= end_date_limit:
            logger.info(
                "[copy_json_data_from_product] Atteinte de la limite de temps (%s). Arrêt du traitement.",
                end_date_limit.strftime("%d/%m/%Y %H:%M:%S"),
            )
            break

        last_ids = ids
        if i < chunk_start:
            i = i + 1
            continue
        attempts = 0
        start_time = time.perf_counter()
        while attempts < max_attempts:
            if (i % NB_LOGS) == 0:
                logger.info("[copy_json_data_from_product] Tentative %d pour l'itération %d", (attempts + 1), i)
            try:
                ids_in = ",".join([str(id) for id in ids])
                keys = [
                    "author",
                    "ean",
                    "gtl_id",
                    "rayon",
                    "code_clil",
                    "dewey",
                    "titelive_regroup",
                    "prix_livre",
                    "schoolbook",
                    "top",
                    "collection",
                    "num_in_collection",
                    "comment",
                    "editeur",
                    "date_parution",
                    "distributeur",
                    "bookFormat",
                ]
                for key in keys:
                    key_replace = "'{" + key + "}'"
                    sql = f"""
                    UPDATE offer 
                      SET "name" = product."name", 
                          "description" = product."description", 
                          "jsonData" = jsonb_set(
                              COALESCE(offer."jsonData", product."jsonData"),
                              {key_replace},
                              to_jsonb(product."jsonData"->>'{key}'),
                              true
                          ) 
                      FROM product 
                      WHERE product.id = offer."productId" 
                      AND product.id IN ({ids_in})
                      AND product."jsonData"->>'{key}' IS NOT NULL;
                    """
                    db.session.execute(sql)
                db.session.commit()
                elapsed_per_batch.append(int(time.perf_counter() - start_time))
                eta = _get_eta(nb_chunks, i, elapsed_per_batch, batch_size)
                if (i % NB_LOGS) == 0:
                    logger.info(
                        "[copy_json_data_from_product] BATCH : id from %d/%d with %d tentatives | eta = %s",
                        i,
                        nb_chunks,
                        attempts,
                        eta,
                    )
                break  # Si réussi, sortez de la boucle de réessai
            except OperationalError as e:
                db.session.rollback()
                attempts += 1
                if (i % NB_LOGS) == 0:
                    logger.info(
                        "[copy_json_data_from_product] Tentative %d pour l'itération %d échouée (Erreur: %s)",
                        attempts,
                        i,
                        e,
                    )
                if attempts < max_attempts:
                    # Attente de 3 minutes avant de réessayer
                    time.sleep(180)
        else:
            # Si nous avons atteint le nombre maximum de tentatives sans succès, quittez la boucle principale
            logger.info(
                "[copy_json_data_from_product] Échec après %d tentatives pour l'itération %d dernier id non traité : %s",
                attempts,
                i,
                ids[:1],
            )
            break
        if (i % NB_LOGS) == 0:
            logger.info("[copy_json_data_from_product] Réussite pour l'itération %d last id %s", i, ids[-1:])
        i = i + 1

    end_date = datetime.datetime.utcnow()

    duration = end_date - start_date

    # Extract days, hours, and minutes from the duration
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format the duration
    formatted_duration = "{:02} days, {:02} hours, {:02} minutes".format(days, hours, minutes)
    logger.info(
        "[copy_json_data_from_product] fin à l'itération %d : %s : %s -> last id : %s",
        i,
        end_date.strftime("%d/%m/%Y %H:%M:%S"),
        formatted_duration,
        last_ids[:1],
    )


def copy_json_data_from_product(batch_size, chunk_start) -> None:
    logger.info("[copy_json_data_from_product] start")
    logger.info("Si besoin, fixez la date limite à une date spécifique (jour/heure).")
    with app.app_context():
        _fix_offers(batch_size, chunk_start)


copy_json_data_from_product(1000, 0)
