import logging
from time import time

import click

import pcapi.core.providers.repository as providers_repository
from pcapi.local_providers import provider_manager
from pcapi.utils.blueprint import Blueprint

from . import models
from . import tasks
from .titelive_utils import generate_titelive_gtl_from_file


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("synchronize_venue_providers_apis")
def synchronize_venue_providers_apis() -> None:
    _synchronize_venue_providers_apis()


def _synchronize_venue_providers_apis() -> None:
    # FIXME(viconnex): we should joinedload(Provider.venueProviders) to avoir N+1 queries but sqlalchemy is not able to build the request
    providers_apis = models.Provider.query.filter(
        models.Provider.isActive,
        models.Provider.apiUrl.is_not(None),
    ).all()

    for provider in providers_apis:
        venue_provider_ids = [
            venue_provider.id for venue_provider in provider.venueProviders if venue_provider.isActive
        ]

        if provider.enableParallelSynchronization:
            for venue_provider_id in venue_provider_ids:
                logger.info(
                    "Enqueuing synchronization with parallel mode",
                    extra={"provider": provider.name, "venue_provider": venue_provider_id},
                )
                tasks.synchronize_venue_providers_task.delay(
                    tasks.SynchronizeVenueProvidersRequest(
                        provider_id=provider.id,
                        venue_provider_ids=[venue_provider_id],
                    )
                )
        else:
            logger.info(
                "Enqueuing synchronization without parallel mode",
                extra={"provider": provider.name, "venue_count": len(venue_provider_ids)},
            )
            tasks.synchronize_venue_providers_task.delay(
                tasks.SynchronizeVenueProvidersRequest(
                    provider_id=provider.id,
                    venue_provider_ids=venue_provider_ids,
                )
            )


@blueprint.cli.command("update_providables")
@click.option("-p", "--provider-name", help="Limit update to this provider name")
@click.option(
    "-l",
    "--limit",
    help="Limit update to n items per providerName/venueId" + " (for test purposes)",
    type=int,
    default=None,
)
@click.option("-w", "--venue-provider-id", type=int, help="Limit update to this venue provider id")
def update_providables(provider_name: str, venue_provider_id: int, limit: int) -> None:
    start = time()
    logger.info(
        "Starting update_providables with provider_name=%s and venue_provider_id=%s", provider_name, venue_provider_id
    )

    if (provider_name and venue_provider_id) or not (provider_name or venue_provider_id):
        raise ValueError("Call either with provider-name or venue-provider-id")

    if provider_name:
        provider_manager.synchronize_data_for_provider(provider_name, limit)

    if venue_provider_id:
        venue_provider = providers_repository.get_venue_provider_by_id(venue_provider_id)
        provider_manager.synchronize_venue_provider(venue_provider, limit)

    logger.info(
        "Finished update_providables with provider_name=%s and venue_provider_id=%s elapsed=%.2f",
        provider_name,
        venue_provider_id,
        time() - start,
    )


@blueprint.cli.command("update_providables_by_provider_id")
@click.option("-p", "--provider-id", required=True, help="Update providables for this provider", type=int)
@click.option(
    "-l", "--limit", help="Limit update to n items per venue provider" + " (for test purposes)", type=int, default=None
)
def update_providables_by_provider_id(provider_id: int, limit: int | None) -> None:
    venue_providers = providers_repository.get_active_venue_providers_by_provider(provider_id)
    provider_manager.synchronize_venue_providers(venue_providers, limit)


@blueprint.cli.command("update_gtl")
@click.option("-f", "--file", required=True, help="CSV extract of GTL_2023.xlsx with tab as separator", type=str)
def update_gtl(file: str) -> None:
    generate_titelive_gtl_from_file(file)
    # TODO we can later automatically reindex only the offers for which the gtl changed


# FIXME (cepehang, 2023-09-25) delete from codebase after use
@blueprint.cli.command("import_titelive_music")
@click.option(
    "-f",
    "--file",
    default="/tmp/titelive_music.csv",
    help="Titelive music CSV, free of null characters and of duplicates",
    type=str,
)
@click.option("-l", "--from-line", default=1, help="Line from which to start importing", type=int)
@click.option("--dry-run", default=False, help="Enable to not persist changes", is_flag=True)
def import_titelive_music(file: str, from_line: int, dry_run: bool) -> None:
    import csv
    import datetime
    import itertools

    from pcapi.connectors import thumb_storage
    from pcapi.connectors import titelive
    from pcapi.core.offers import models as offers_models
    from pcapi.core.providers import constants as providers_constants
    import pcapi.core.providers.models as providers_models
    from pcapi.core.providers.titelive_music_search import is_music_codesupport_allowed
    from pcapi.core.providers.titelive_music_search import parse_titelive_music_codesupport
    from pcapi.core.providers.titelive_music_search import parse_titelive_music_genre
    from pcapi.models import db
    from pcapi.utils import requests

    HEADERS = [
        "artiste",
        "codesupport",
        "commentaire",
        "compositeur",
        "dateparution",
        "dispo",
        "distributeur",
        "editeur",
        "gencod",
        "gtl_first",
        "imagesUrl_recto",
        "interprete",
        "label",
        "nb_galettes",
        "prix",
        "resume",
        "titre",
    ]

    CHUNK_SIZE = 500
    # obtenus grâce à un fichier titelive
    EXPLICIT_CONTENT_EANS = [
        "0008811292324",
        "0012414163622",
        "0016861865580",
        "0016998105634",
        "0016998105658",
        "0016998518410",
        "0016998527245",
        "0044003268197",
        "0044006798226",
        "0075021032910",
        "0075678613692",
        "0075678614392",
        "0075678614620",
        "0075678616433",
        "0075678621857",
        "0075678622410",
        "0075678624971",
        "0075678626098",
        "0075678628733",
        "0075678628801",
        "0075678629204",
        "0075678630194",
        "0075678630668",
        "0075678632457",
        "0075678632525",
        "0075678642203",
        "0075678644191",
        "0075678645662",
        "0075678999147",
        "0093624854517",
        "0093624856870",
        "0093624857020",
        "0093624857143",
        "0093624867623",
        "0093624868286",
        "0093624870708",
        "0093624870715",
        "0093624872245",
        "0093624872719",
        "0093624892137",
        "0093624892144",
        "0093624917199",
        "0093624922810",
        "0093624926269",
        "0190295048600",
        "0190295172060",
        "0190295182533",
        "0190295189136",
        "0190295232177",
        "0190295276775",
        "0190295337834",
        "0190295378356",
        "0190295448332",
        "0190295466701",
        "0190295484088",
        "0190295542979",
        "0190295710828",
        "0190296237744",
        "0190296270758",
        "0190296545061",
        "0190296650659",
        "0190296704710",
        "0190758883618",
        "0190758956220",
        "0190759951620",
        "0190759996829",
        "0191404131916",
        "0191404131923",
        "0192641875717",
        "0194397006124",
        "0194398255927",
        "0194398775623",
        "0194399477229",
        "0194399629727",
        "0194690294532",
        "0194690558054",
        "0194690783944",
        "0194690787362",
        "0194690796579",
        "0194690879838",
        "0194690905063",
        "0194690914232",
        "0194690948985",
        "0194690962417",
        "0194690984174",
        "0196292363555",
        "0196587214623",
        "0196587219628",
        "0196587219727",
        "0196587247720",
        "0196587569419",
        "0196587651329",
        "0196587651411",
        "0196587773618",
        "0196587775827",
        "0196587792121",
        "0196587812324",
        "0196587812416",
        "0196587929527",
        "0196587953324",
        "0196588007521",
        "0196588007828",
        "0196588019920",
        "0196588020025",
        "0196588110122",
        "0196588189326",
        "0196588237423",
        "0196588249310",
        "0196588271427",
        "0196588460326",
        "0197342023474",
        "0197342044059",
        "0197342066167",
        "0197342075893",
        "0197342224567",
        "0197342224673",
        "0197342282390",
        "0197342282406",
        "0600445022324",
        "0600753132852",
        "0600753132869",
        "0600753385470",
        "0600753463772",
        "0600753463802",
        "0600753468210",
        "0600753468920",
        "0600753469958",
        "0600753974087",
        "0600753978856",
        "0602435160887",
        "0602435217406",
        "0602435267494",
        "0602435272856",
        "0602435334066",
        "0602435633169",
        "0602435633176",
        "0602435738901",
        "0602435839820",
        "0602438108978",
        "0602438927685",
        "0602445107049",
        "0602445359615",
        "0602445359622",
        "0602445561544",
        "0602445735334",
        "0602445891801",
        "0602448075437",
        "0602448075567",
        "0602448136800",
        "0602448152398",
        "0602448193582",
        "0602448224330",
        "0602448224385",
        "0602448288240",
        "0602448611079",
        "0602448687494",
        "0602448717870",
        "0602448727206",
        "0602448982773",
        "0602448996183",
        "0602455054142",
        "0602455059390",
        "0602455075611",
        "0602455099969",
        "0602455149527",
        "0602455156044",
        "0602455274779",
        "0602455406620",
        "0602455415851",
        "0602455437471",
        "0602455466877",
        "0602455558954",
        "0602455568809",
        "0602455684141",
        "0602455700001",
        "0602455738790",
        "0602455738998",
        "0602455739049",
        "0602455739070",
        "0602455739988",
        "0602455739995",
        "0602455742971",
        "0602455778949",
        "0602455793973",
        "0602455793997",
        "0602455795328",
        "0602455796363",
        "0602455826206",
        "0602455877659",
        "0602455891648",
        "0602455977625",
        "0602458124118",
        "0602458163728",
        "0602458221602",
        "0602458270235",
        "0602458347975",
        "0602498614747",
        "0602498617410",
        "0602498641361",
        "0602498646700",
        "0602498646748",
        "0602498648841",
        "0602498653364",
        "0602498678107",
        "0602498824047",
        "0602498851272",
        "0602498867709",
        "0602498878934",
        "0602498878965",
        "0602507381752",
        "0602508072291",
        "0602508276309",
        "0602508375118",
        "0602508446733",
        "0602508448898",
        "0602508585562",
        "0602508598531",
        "0602508735165",
        "0602508735172",
        "0602508818387",
        "0602508818400",
        "0602508870293",
        "0602508929915",
        "0602508940347",
        "0602517478527",
        "0602517501478",
        "0602517919211",
        "0602527188386",
        "0602527832623",
        "0602527878409",
        "0602537192267",
        "0602537331246",
        "0602537352227",
        "0602537352234",
        "0602537352241",
        "0602537352265",
        "0602537588114",
        "0602547128034",
        "0602547270917",
        "0602547288790",
        "0602547300683",
        "0602547311009",
        "0602547340986",
        "0602547536341",
        "0602547854032",
        "0602547948229",
        "0602547973474",
        "0602557005769",
        "0602557367843",
        "0602557411461",
        "0602557649697",
        "0602557936735",
        "0602567361510",
        "0602567393849",
        "0602567555780",
        "0602567749967",
        "0602577052354",
        "0602577094927",
        "0602577656897",
        "0602577840630",
        "0603497832033",
        "0603497832057",
        "0603497832934",
        "0603497833108",
        "0603497833641",
        "0603497833672",
        "0603497833719",
        "0603497837120",
        "0603497839445",
        "0603497841301",
        "0603497841363",
        "0606945712826",
        "0606949028725",
        "0606949041328",
        "0606949048624",
        "0606949075927",
        "0606949079024",
        "0606949234423",
        "0606949264123",
        "0606949314729",
        "0606949329013",
        "0606949343620",
        "0634164687120",
        "0634457137745",
        "0634457143500",
        "0673951012523",
        "0677517016918",
        "0677517016925",
        "0693461238527",
        "0693461255029",
        "0724353113810",
        "0724353448806",
        "0731452735928",
        "0756504403327",
        "0756504403426",
        "0756504406427",
        "0760137113805",
        "0769712403829",
        "0810061165194",
        "0810097914704",
        "0810097915145",
        "0810098503051",
        "0810098503068",
        "0810098505130",
        "0810555021289",
        "0810555022347",
        "0822720700165",
        "0848928097104",
        "0881034122773",
        "0887828036912",
        "0887828046010",
        "0888072175419",
        "0888072474581",
        "0888430777521",
        "0888750441126",
        "0888751698512",
        "0888915181386",
        "0888915223147",
        "0888915329498",
        "0888915350775",
        "0888915370162",
        "0888915403365",
        "0888915408292",
        "0888915573785",
        "0888915670439",
        "0888915674352",
        "0888915795194",
        "0888915855720",
        "0889853777112",
        "0889854344115",
        "3232822262091",
        "3516628431821",
        "3516628431920",
        "3516628432019",
        "3516628433023",
        "3521383473665",
        "3664216015592",
        "3664216024778",
        "3664216028134",
        "3664216028660",
        "3664216028738",
        "3664216033558",
        "3664216037150",
        "3664216037594",
        "3664216038621",
        "3664216045100",
        "3700187670498",
        "3700187673512",
        "3700187675233",
        "3700187675318",
        "3700187676858",
        "3700187677084",
        "3700187677855",
        "3700187678043",
        "3700187678128",
        "3700187679507",
        "3700187680275",
        "3700187680299",
        "3700187680428",
        "3700187681234",
        "3700187681418",
        "3700187681425",
        "3700187681524",
        "3700187681661",
        "3700187681692",
        "3700187681746",
        "3700551782192",
        "3700551782420",
        "3700604713876",
        "3701216806123",
        "3701270201568",
        "3760068973438",
        "3760068973445",
        "3760347745442",
        "3760370260257",
        "4029759173182",
        "4050538664423",
        "4050538664454",
        "4050538764581",
        "4050538820836",
        "4050538860184",
        "4050538860191",
        "4050538870527",
        "4050538889048",
        "4050538889055",
        "4050538889079",
        "4050538919004",
        "4050538964929",
        "4065629623043",
        "4251648410171",
        "5053760093176",
        "5054197153105",
        "5054197153136",
        "5054197160943",
        "5054197280085",
        "5054197352324",
        "5054197352331",
        "5054197477898",
        "5054197498404",
        "5054197506956",
        "5054197558085",
        "5054197584046",
        "5054197584077",
        "5054197595905",
        "5056167119715",
        "5056167176930",
        "5056321634634",
        "5056321695123",
        "5060330570906",
        "5060766763873",
        "5099751879220",
        "5099951415723",
        "5400863014483",
        "5400863055219",
        "7350126740520",
        "7350126740537",
        "7350126740544",
        "8714092784428",
        "8714092784435",
        "8714092784442",
        "8718627232613",
        "8718627236079",
        "8719262028449",
    ]

    def import_titelive_music_csv(dry_run: bool, file: str, from_line: int = 1) -> None:
        """Imports Titelive music CSV starting from_line with headers included"""
        provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        with open(file, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            headers = next(csv_reader)
            assert headers == HEADERS, f"{headers =} {HEADERS =}"

            line_number = 1 if from_line < 2 else from_line - 1
            skipped = 0 if line_number < 1 else line_number - 1
            titelive_products_to_save = []
            try:
                for row in itertools.islice(csv_reader, skipped, None):
                    line_number += 1
                    titelive_product = dict(zip(HEADERS, row))
                    if not is_music_codesupport_allowed(titelive_product["codesupport"]):
                        skipped += 1
                        continue
                    titelive_products_to_save.append(titelive_product)

                    if len(titelive_products_to_save) == CHUNK_SIZE:
                        save_titelive_products(titelive_products_to_save, provider, dry_run)
                        logger.info(
                            "titelive music csv successfully imported up to line %s including %s ignored",
                            line_number,
                            skipped,
                        )
                        titelive_products_to_save = []

                if titelive_products_to_save:
                    save_titelive_products(titelive_products_to_save, provider, dry_run)
                    logger.info(
                        "titelive music csv successfully imported up to line %s including %s ignored",
                        line_number,
                        skipped,
                    )

                end_sync_event = providers_models.LocalProviderEvent(
                    date=datetime.datetime(2023, 9, 4),  # generation date of the extract
                    payload=titelive.TiteliveBase.MUSIC.value,
                    provider=provider,
                    type=providers_models.LocalProviderEventType.SyncEnd,
                )
                db.session.add(end_sync_event)
                if dry_run:
                    db.session.rollback()
                else:
                    db.session.commit()
                logger.info("titelive music csv successfully imported")

            except Exception as e:
                logger.exception(
                    "failed between line %s and line %s",
                    line_number - CHUNK_SIZE + 1,
                    line_number,
                )
                raise e

    def save_titelive_products(
        titelive_products: list[dict],
        provider: providers_models.Provider,
        dry_run: bool,
    ) -> None:
        already_existing_products = offers_models.Product.query.filter(
            offers_models.Product.idAtProviders.in_([p["gencod"].zfill(13) for p in titelive_products])
        ).all()
        already_existing_product_ids = [p.idAtProviders for p in already_existing_products]
        if already_existing_product_ids:
            logger.warning(
                "ignoring titelive music EANs %s because they already exist in db",
                ", ".join(already_existing_product_ids),
            )

        titelive_products = [p for p in titelive_products if p["gencod"].zfill(13) not in already_existing_product_ids]
        products_to_save = [build_product(titelive_product, provider) for titelive_product in titelive_products]
        db.session.add_all(products_to_save)
        if dry_run:
            db.session.rollback()
            return

        db.session.commit()

        titelive_thumbnail_by_ean = {
            titelive_product["gencod"].zfill(13): titelive_product["imagesUrl_recto"]
            for titelive_product in titelive_products
        }
        for product in products_to_save:
            assert product.extraData, "product %s initialized without extra data" % product.id

            ean = product.extraData.get("ean")
            assert ean, "product %s initialized without ean" % product.id

            new_thumbnail_url = titelive_thumbnail_by_ean.get(ean)
            if not new_thumbnail_url:
                continue

            try:
                image_bytes = titelive.download_titelive_image(new_thumbnail_url)
                if product.thumbCount > 0:
                    thumb_storage.remove_thumb(product, storage_id_suffix="")
                thumb_storage.create_thumb(product, image_bytes, storage_id_suffix_str="", keep_ratio=True)
            except requests.ExternalAPIException as e:
                logger.error(
                    "Error while downloading Titelive image",
                    extra={
                        "exception": e,
                        "url": new_thumbnail_url,
                        "request_type": "image",
                    },
                )
                continue

    def build_product(titelive_product: dict, provider: providers_models.Provider) -> offers_models.Product:
        ean = titelive_product["gencod"].zfill(13)
        gtl_id = titelive_product["gtl_first"].zfill(6).ljust(8, "0")
        music_type, music_subtype = parse_titelive_music_genre(gtl_id)
        return offers_models.Product(
            description=titelive_product.get("resume"),
            idAtProviders=ean,
            lastProvider=provider,
            name=titelive_product["titre"],
            subcategoryId=parse_titelive_music_codesupport(titelive_product["codesupport"]).id,
            extraData=offers_models.OfferExtraData(
                artist=titelive_product["artiste"],
                author=titelive_product.get("compositeur"),
                comment=titelive_product.get("commentaire"),
                contenu_explicite="1" if ean in EXPLICIT_CONTENT_EANS else "0",
                date_parution=datetime.datetime.strptime(titelive_product["dateparution"], "%Y-%m-%d %H:%M:%S")
                .date()
                .isoformat(),
                dispo=titelive_product["dispo"],
                distributeur=titelive_product["distributeur"],
                ean=ean,
                editeur=titelive_product["editeur"],
                gtl_id=gtl_id,
                music_label=titelive_product["label"],
                musicSubType=str(music_subtype.code),
                musicType=str(music_type.code),
                nb_galettes=titelive_product["nb_galettes"],
                performer=titelive_product.get("interprete"),
            ),
        )

    import_titelive_music_csv(file=file, dry_run=dry_run, from_line=from_line)
