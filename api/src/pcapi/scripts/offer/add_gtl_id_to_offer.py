import datetime
import enum
import logging
import statistics
import time

import pytz

from pcapi.models import db


BATCH_SIZE = 1000

logger = logging.getLogger(__name__)


class OfferOrProduct(str, enum.Enum):
    OFFER = "offer"
    PRODUCT = "product"


def _get_eta(end_id: int, current: int, elapsed_per_batch: list) -> str:
    left_to_do = end_id - current
    eta = left_to_do / BATCH_SIZE * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


def set_gtl_id_in_db(table_name: OfferOrProduct, start_id: int, end_id: int, dry_run: bool = True) -> None:
    elapsed_per_batch = []
    logger.info("[fix_product_gtl_id_titelive] BATCH_SIZE : %d", BATCH_SIZE)
    for i in range(start_id, end_id, BATCH_SIZE):
        start_time = time.perf_counter()
        db.session.execute(
            f"""
            UPDATE {table_name.value}
            SET "jsonData" = jsonb_set(
                {table_name.value}."jsonData",
                '{{gtl_id}}',
                    to_jsonb(CASE 
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '501'
                            THEN
                                '02000000' 
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '520'
                            THEN
                                '02000000'    
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '530'
                            THEN
                                '12000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '600'
                            THEN
                                '01000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '700'
                            THEN
                                '13000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '800'
                            THEN
                                '05000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '820'
                            THEN
                                '06000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '840'
                            THEN
                                '07000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '850'
                            THEN
                                '08000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '860'
                            THEN
                                '14000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '870'
                            THEN
                                '14000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '880'
                            THEN
                                '04000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '900'
                            THEN
                                '11000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '930'
                            THEN
                                '02000000'
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '1000'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '1001' THEN '17000000'
                                    ELSE '09000000'
                                END
                        ELSE '19000000'   
                    END)              
                ,
                true
            ) WHERE {table_name.value}.id between :start and :end
              AND {table_name.value}."subcategoryId" in ('CONCERT', 'EVENEMENT_MUSIQUE',
                'LIVESTREAM_MUSIQUE', 'ABO_CONCERT', 'FESTIVAL_MUSIQUE',
                'SUPPORT_PHYSIQUE_MUSIQUE_CD', 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
                'TELECHARGEMENT_MUSIQUE', 'ABO_PLATEFORME_MUSIQUE', 'CAPTATION_MUSIQUE')
              AND {table_name.value}."jsonData" is not null AND {table_name.value}."jsonData" ->> 'musicType' is not null
            """,
            params={"start": i, "end": i + BATCH_SIZE},
        )
        if dry_run:
            db.session.rollback()
        else:
            db.session.commit()
            if i % 20_000_000 == 0:  #  VACUUM every 20_000_000 rows
                # Why and how it works: https://wiki.postgresql.org/wiki/Introduction_to_VACUUM,_ANALYZE,_EXPLAIN,_and_COUNT#Vacuum_the_Dirt_out_of_Your_Database
                db.session.execute("VACUUM")
                db.session.commit()

        elapsed_per_batch.append(int(time.perf_counter() - start_time))
        eta = _get_eta(end_id, i, elapsed_per_batch)

        logger.info("[fix_%s_gtl_id_titelive] BATCH : id from %d | eta = %s", table_name.value, i, eta)


def execute_offer_script(min_id: int, dry_run: bool = True) -> None:
    logger.info("[fix_offer_gtl_id_titelive] Start OFFER: total_rows = 17_579_312")
    max_id = 100000001  # int(input("enter max offer id: "))
    set_gtl_id_in_db(OfferOrProduct.OFFER, start_id=min_id, end_id=max_id, dry_run=dry_run)


def execute_product_script(dry_run: bool = True) -> None:
    logger.info("[fix_product_gtl_id_titelive] Start PRODUCT: total rows = 928_492")
    min_id = int(input("enter min product id: "))
    max_id = int(input("enter max product id: "))
    set_gtl_id_in_db(OfferOrProduct.PRODUCT, start_id=min_id, end_id=max_id, dry_run=dry_run)


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        execute_offer_script(min_id=94708001, dry_run=False)
