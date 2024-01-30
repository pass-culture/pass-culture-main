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
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '502' THEN '02030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '503' THEN '02030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '504' THEN '02010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '505' THEN '02010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '506' THEN '02010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '507' THEN '02030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '508' THEN '02030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '509' THEN '02010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '510' THEN '02010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '511' THEN '02040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '512' THEN '02030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '513' THEN '02040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '514' THEN '02010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '515' THEN '02070000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '516' THEN '02010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '517' THEN '02020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '518' THEN '02010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '519' THEN '02010000'
                                    ELSE '02010000' 
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '520'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '521' THEN '02050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '522' THEN '02050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '523' THEN '02050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '524' THEN '02050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '525' THEN '02050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '526' THEN '02050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '527' THEN '02050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '528' THEN '02050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '529' THEN '02050000'
                                    ELSE '02050000'    
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '530'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '531' THEN '12010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '532' THEN '12060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '533' THEN '12040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '534' THEN '12010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '535' THEN '12050000'
                                    ELSE '12000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '600'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '601' THEN '01120000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '602' THEN '01050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '603' THEN '01090000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '604' THEN '01090000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '605' THEN '01120000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '606' THEN '01000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '607' THEN '01000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '608' THEN '01010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '609' THEN '01120000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '610' THEN '01120000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '611' THEN '01040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '612' THEN '01090000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '613' THEN '01000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '614' THEN '01000000'
                                    ELSE '01000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '700'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '701' THEN '13030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '702' THEN '13030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '703' THEN '13030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '704' THEN '13060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '705' THEN '13050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '706' THEN '13110000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '707' THEN '13070000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '708' THEN '13060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '709' THEN '13060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '710' THEN '13060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '711' THEN '13050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '712' THEN '13040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '713' THEN '13000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '714' THEN '13090000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '715' THEN '13060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '716' THEN '13110000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '717' THEN '13010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '718' THEN '13070000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '719' THEN '13060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '720' THEN '13020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '721' THEN '13060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '722' THEN '13110000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '723' THEN '13110000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '724' THEN '13110000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '725' THEN '13050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '726' THEN '13110000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '727' THEN '13110000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '728' THEN '13010000'
                                    ELSE '13000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '800'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '801' THEN '05030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '802' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '803' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '804' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '805' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '806' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '808' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '809' THEN '05080000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '810' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '812' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '813' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '814' THEN '05000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '815' THEN '05000000'
                                    ELSE '05000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '820'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '821' THEN '06040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '823' THEN '06010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '824' THEN '06010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '825' THEN '06010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '827' THEN '06010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '829' THEN '06010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '831' THEN '06040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '832' THEN '06030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '834' THEN '06030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '835' THEN '06010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '836' THEN '06010000'
                                    ELSE '06000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '840'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '842' THEN '07040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '843' THEN '07040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '844' THEN '08050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '845' THEN '07000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '846' THEN '07000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '847' THEN '07040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '848' THEN '08060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '849' THEN '07020000'
                                    ELSE '07000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '850'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '851' THEN '08010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '852' THEN '08010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '853' THEN '08010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '854' THEN '08010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '855' THEN '08010000'
                                    ELSE '08000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '860'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '861' THEN '14030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '862' THEN '14030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '864' THEN '14030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '865' THEN '14030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '866' THEN '14030000'
                                    ELSE'14000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '870'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '871' THEN '14020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '872' THEN '14020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '873' THEN '14050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '874' THEN '14010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '875' THEN '14010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '876' THEN '14010000'
                                    ELSE '14000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '880'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '881' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '882' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '883' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '884' THEN '04070000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '885' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '886' THEN '04060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '887' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '888' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '889' THEN '04010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '890' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '891' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '892' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '893' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '894' THEN '04030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '895' THEN '04000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '896' THEN '04050000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '897' THEN '04020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '898' THEN '04000000'
                                    ELSE '04000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '900'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '901' THEN '11000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '903' THEN '11000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '905' THEN '11020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '906' THEN '11040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '907' THEN '11020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '908' THEN '11000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '909' THEN '11030000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '910' THEN '11010000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '911' THEN '11000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '912' THEN '11020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '913' THEN '11000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '914' THEN '11000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '921' THEN '10000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '922' THEN '10090000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '923' THEN '11000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '924' THEN '10000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '925' THEN '10000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '926' THEN '11020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '927' THEN '11000000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '928' THEN '11000000'
                                    ELSE '11000000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '930'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '931' THEN '02060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '932' THEN '02060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '933' THEN '02060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '934' THEN '02060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '935' THEN '02060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '936' THEN '02060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '937' THEN '02060000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '938' THEN '02060000'
                                    ELSE '02060000'
                                END
                        WHEN {table_name.value}."jsonData" ->> 'musicType' = '1000'
                            THEN
                                CASE
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '1001' THEN '17040000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '1002' THEN '09020000'
                                    WHEN {table_name.value}."jsonData" ->> 'musicSubType' = '1006' THEN '09020000'
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
