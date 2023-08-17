import logging
import random

from pcapi.core.categories import subcategories_v2
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.providers.titelive_gtl import GTLS
from pcapi.domain.music_types import MUSIC_SUB_TYPES_BY_SLUG
from pcapi.domain.music_types import MUSIC_TYPES_BY_SLUG
from pcapi.domain.music_types import music_types
from pcapi.domain.titelive import read_things_date
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_AUTHOR_NAMES
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_DESCRIPTIONS
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_FIRST_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_LAST_NAMES


logger = logging.getLogger(__name__)


THINGS_PER_SUBCATEGORY = 7


def create_industrial_thing_products() -> dict[str, offers_models.Product]:
    logger.info("create_industrial_thing_products")

    thing_products_by_name = {}

    thing_subcategories = [s for s in subcategories_v2.ALL_SUBCATEGORIES if not s.is_event]

    id_at_providers = 1234

    base_ean = 1234567890123

    for product_creation_counter in range(0, THINGS_PER_SUBCATEGORY):
        for thing_subcategories_list_index, thing_subcategory in enumerate(thing_subcategories):
            mock_index = (product_creation_counter + thing_subcategories_list_index) % len(MOCK_NAMES)

            name = "{} / {}".format(thing_subcategory.id, MOCK_NAMES[mock_index])
            is_online_only = thing_subcategory.is_online_only
            url = "https://ilestencoretemps.fr/" if is_online_only else None

            thing_product = offers_factories.ProductFactory(
                extraData={"author": MOCK_AUTHOR_NAMES[mock_index]},
                description=MOCK_DESCRIPTIONS[mock_index],
                idAtProviders=str(id_at_providers),
                isNational=is_online_only,
                name=MOCK_NAMES[mock_index],
                subcategoryId=thing_subcategory.id,
                url=url,
            )

            extraData = {}
            extra_data_index = 0
            for conditionalField_name in thing_product.subcategory.conditional_fields:
                conditional_index = product_creation_counter + thing_subcategories_list_index + extra_data_index
                if conditionalField_name in [
                    subcategories_v2.ExtraDataFieldEnum.AUTHOR.value,
                    subcategories_v2.ExtraDataFieldEnum.PERFORMER.value,
                    subcategories_v2.ExtraDataFieldEnum.SPEAKER.value,
                    subcategories_v2.ExtraDataFieldEnum.STAGE_DIRECTOR.value,
                ]:
                    mock_first_name_index = (
                        product_creation_counter + thing_subcategories_list_index + extra_data_index
                    ) % len(MOCK_FIRST_NAMES)
                    mock_first_name = MOCK_FIRST_NAMES[mock_first_name_index]
                    mock_last_name_index = (
                        product_creation_counter + thing_subcategories_list_index + extra_data_index
                    ) % len(MOCK_LAST_NAMES)
                    mock_last_name = MOCK_LAST_NAMES[mock_last_name_index]
                    mock_name = "{} {}".format(mock_first_name, mock_last_name)
                    extraData[conditionalField_name] = mock_name
                elif conditionalField_name == "musicType":
                    music_type_index: int = conditional_index % len(music_types)
                    music_type = music_types[music_type_index]
                    extraData[conditionalField_name] = str(music_type.code)
                    music_sub_type_index: int = conditional_index % len(music_type.children)
                    music_sub_type = music_type.children[music_sub_type_index]
                    extraData["musicSubType"] = str(music_sub_type.code)
                elif conditionalField_name == "ean":
                    extraData["ean"] = str(base_ean)
                    base_ean += 1
                elif conditionalField_name == "gtl_id":
                    extraData["gtl_id"] = random.choice(list(GTLS.keys()))
                extra_data_index += 1
            thing_product.extraData = extraData
            thing_products_by_name[name] = thing_product
            id_at_providers += 1

        product_creation_counter += len(thing_subcategories)

    titelive_synced_products = create_titelive_synced_music_products()
    thing_products_by_name |= {product.name: product for product in titelive_synced_products}

    repository.save(*thing_products_by_name.values())

    logger.info("created %d thing products", len(thing_products_by_name))

    return thing_products_by_name


def create_titelive_synced_music_products() -> list[offers_models.Product]:
    logger.info("create_titelive_synced_music_products")

    unavailable_cd = offers_factories.ProductFactory(
        description=None,
        extraData=offers_models.OfferExtraData(
            artist="Queen",
            author="Queen",
            comment="Limited Edition",
            disponibility="Indisponible",
            distributeur="Universal Music France",
            ean="0602438073177",
            editeur="VIRGIN RECORDS FRANCE",
            gtl_id="70100",
            music_label="UNIVERSAL MUSIC",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["ROCK-HARD_ROCK"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["ROCK-HARD_ROCK"].code),
            nb_galettes="1",
            performer="Queen",
        ),
        idAtProviders="0602438073177",
        name="Greatest Hits",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    soon_released_cd = offers_factories.ProductFactory(
        description="Après les récentes rééditions de The Who 'Sell Out', 'My Generation', 'Tommy' et 'Quadrophenia', voici enfin Who's Next, considéré par de nombreux fans comme le plus grand album du groupe ! Découvrez cette nouvelle réédition déclinée en plusieurs supports : CD Cristal, 2CD Digipack, LP, Coffret 10CD+Blu-ray Audio ainsi qu'un coffret 4LP (album rematerisé Who's Next et le Live At The Civic Auditorium, San Francisco -1971).\n\nLe processus de création de l'album fut à l'époque révolutionnaire. Au début des années 70, The Who, et en particulier leur principal auteur-compositeur Pete Townshend, ont été confrontés à un immense défi : Comment succéder au succès international de Tommy ? La réponse a été un projet ambitieux, futuriste et prémonitoire nommé 'Life House'. Life House prédisait un monde dystopique qui semble aujourd'hui familier. Les thèmes abordés étaient ceux de la pollution, des entreprises trop puissantes et de la technologie. Le projet en deux volets réunissait un film et une performance live au Young Vic Theatre de Londres.\n\nEt comme l'écrit Pete Townshend « La fiction et l'expérience Live étaient toutes deux imparfaites, et aucune n'a été correctement réalisée. Mais une musique merveilleuse est sortie du projet, et l'idée m'a toujours hantée, car de nombreux éléments de la fiction semblent se réaliser »\n",
        extraData=offers_models.OfferExtraData(
            artist="The who",
            author="The who",
            comment="TBC",
            date_parution=read_things_date("15/09/2023"),
            disponibility="À paraître",
            distributeur="Universal Music France",
            ean="0602435858395",
            editeur="UNIVERSAL",
            gtl_id="70100",
            music_label="UNIVERSAL",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["ROCK-HARD_ROCK"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["ROCK-HARD_ROCK"].code),
            nb_galettes="1",
            performer="The Who",
        ),
        idAtProviders="0602435858395",
        name="Who's Next",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    available_rap_cd_1 = offers_factories.ProductFactory(
        description='GIMS revient avec " Les dernières volontés de Mozart ", un album de tubes.\n\n" Les dernières volontés de Mozart " est un album phénomène.\nWolfgang Amadeus Mozart ne rentrait dans aucune case, il a composé et excellé dans tous les registres de son époque. Son audace, sa virtuosité et son génie sont inégalables et traversent le temps.\nD\'une créativité rare, GIMS relève encore une fois le défi : celui d\'avoir composé des morceaux aux univers tous différents, à la fois populaires et toujours innovants. Ce nouvel opus est d\'une qualité redoutable, rassemblant 20 titres qui sont autant de tubes en devenir.\nEt pour que la surprise soit totale, l\'album offre des collaborations aussi réussies qu\'inattendues...\nInclus le tube " Maintenant ".\n',
        extraData=offers_models.OfferExtraData(
            artist="Gims",
            author="Gims",
            date_parution=read_things_date("02/12/2022"),
            disponibility="Disponible",
            distributeur="Believe",
            ean="3700187679323",
            editeur="BELIEVE",
            gtl_id="110400",
            music_label="PLAY TWO",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code),
            nb_galettes="1",
            performer="Gims",
        ),
        idAtProviders="3700187679323",
        name="Les dernières volontés de Mozart (symphony)",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    available_rap_cd_2 = offers_factories.ProductFactory(
        description='.Après l\'immense succès de " Civilisation " (déjà plus de 600.000 ventes) et de la nouvelle saison de la série-documentaire " Montre jamais ça à personne ", OrelSan revient avec une version augmentée de 10 nouveaux titres de son album déjà culte : "Civilisation Edition Ultime".\n\nAvec près de 2,5 millions d\'albums vendus en cumulé et 9 Victoires de la Musique, OrelSan occupe une place à part dans le paysage français. La voix d\'une génération.\n\nOrelSan " Civilisation Edition Ultime ", double album CD.\n',
        extraData=offers_models.OfferExtraData(
            artist="Orelsan",
            author="Orelsan",
            comment="édition double CD sous fourreau",
            date_parution=read_things_date("28/10/2022"),
            disponibility="Disponible",
            distributeur="Wagram Music",
            ean="3596974281424",
            editeur="3EME BUREAU",
            gtl_id="110400",
            music_label="3EME BUREAU",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["HIP_HOP_RAP-RAP_FRANCAIS"].code),
            nb_galettes="2",
            performer="Orelsan",
        ),
        idAtProviders="3596974281424",
        name="Civilisation - Edition ultime",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    available_multiple_discs_cd = offers_factories.ProductFactory(
        description="PROJET CARITATIF, A BUT NON LUCRATIF :\n\nTOUS LES PROFITS SERONT REVERSES A L’ASSOCIATION LES RESTOS DU COEUR\n  \nFidèles à l’appel lancé par Coluche dès 1985, et après 2 ans de concerts sans public, les plus grands artistes de la scène musicale française se réunissent pour la cause des Restos du Coeur.\n\nPlus que jamais, les Restos du Coeur ont besoin de vous !\nEt rappelez-vous que « CHAQUE CD OU DVD VENDU = 17 REPAS OFFERTS AUX RESTOS DU COEUR ».\n\nRetrouvez L’INTEGRALITE DU SPECTACLE « 2023 Enfoirés un jour, toujours ».\nInclus le single « Rêvons » écrit et composé par Amir, Nazim et Nyadjiko.",
        extraData=offers_models.OfferExtraData(
            artist="Les enfoirés",
            author="Les enfoirés",
            date_parution=read_things_date("04/03/2023"),
            disponibility="Disponible",
            distributeur="Sony Music Entertainement",
            ean="0196587966423",
            editeur="SONY MUSIC CATALOGUE",
            gtl_id="50200",
            music_label="COLUMBIA",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["CHANSON_VARIETE-CHANSON_FRANCAISE"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["CHANSON_VARIETE-CHANSON_FRANCAISE"].code),
            nb_galettes="2",
            performer="Les Enfoirés",
        ),
        idAtProviders="0196587966423",
        name="2023 Enfoirés un jour, toujours",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    available_french_cd = offers_factories.ProductFactory(
        description="'Coeur Encore' est la nouvelle édition limitée du dernier album de Clara Luciani, déjà certifié triple disque de platine. Après deux Victoires de la Musique en 2022 (Artiste féminine et Meilleur album) l'artiste rend hommage au son qui a bercé la création de son album 'Coeur', en reprenant en français 4 titres légendaires du disco funk dont 'Celebration' en featuring avec Kool & The Gang.",
        extraData=offers_models.OfferExtraData(
            artist="Clara luciani",
            author="Clara luciani",
            date_parution=read_things_date("25/11/2022"),
            disponibility="Disponible",
            distributeur="Universal Music France",
            ean="0602448125255",
            editeur="ROMANCE MUSIQUE",
            gtl_id="50200",
            music_label="ROMANCE MUSIQUE",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["CHANSON_VARIETE-CHANSON_FRANCAISE"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["CHANSON_VARIETE-CHANSON_FRANCAISE"].code),
            nb_galettes="2",
            performer="Clara Luciani",
        ),
        idAtProviders="0602448125255",
        name="Coeur Encore",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    available_pop_vinyl_1 = offers_factories.ProductFactory(
        description="LE GROUPE INTERNATIONAL N°1 DE RETOUR AVEC UN ALBUM DE TUBES POP ! NEUVIÈME ALBUM STUDIO DU QUATUOR BRITANNIQUE, PRODUIT PAR MAX MARTIN ET PORTÉ PAR LE SINGLE 'HIGHER POWER' LANCÉ AU PRINTEMPS 2021 DEPUIS LA STATION SPATIALE INTERNATIONALE AVEC L'AIDE DE THOMAS PESQUET.\nLe quatuor britannique s'apprête à sortir leur neuvième album studio, 'Music Of The Spheres', produit par le producteur star de nombreuses fois récompensé Max Martin, et introduit avec le single \"Higher Power\", ritournelle pop optimiste et entraînante lancée depuis la Station Spatiale Internationale par Thomas Pesquet. Sur le thème graphique de l'espace, Coldplay livre un nouvel opus pop taillé pour les stades, fait à la fois d'hymnes entraînants et de ballades chaleureuses.",
        extraData=offers_models.OfferExtraData(
            artist="Coldplay",
            author="Coldplay",
            date_parution=read_things_date("15/10/2021"),
            disponibility="Disponible",
            distributeur="Warner Music France",
            ean="0190296666964",
            editeur="WEA",
            gtl_id="50300",
            music_label="PARLOPHONE",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["POP-POP_ROCK"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["POP-POP_ROCK"].code),
            nb_galettes="1",
            performer="Coldplay",
        ),
        idAtProviders="0190296666964",
        name="Music Of The Spheres",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    available_pop_vinyl_2 = offers_factories.ProductFactory(
        description="Ce huitième album studio de Gorillaz est une collection énergique, optimiste et riche en genres de 10 titres mettant en vedette un line-up stellaire de collaborateurs : Thundercat, Tame Impala, Bad Bunny, Stevie Nicks, Adeleye Omotayo, Bootie Brown et Beck. Enregistré à Londres et à Los Angeles plus tôt, il est produit par Gorillaz, Remi Kabaka jr. et le producteur de multiples fois récompensé Greg Kurstin.",
        extraData=offers_models.OfferExtraData(
            artist="Gorillaz",
            author="Gorillaz",
            date_parution=read_things_date("24/02/2023"),
            disponibility="Disponible",
            distributeur="Warner Music France",
            ean="5054197199738",
            editeur="WARNER MUSIC UK",
            gtl_id="50300",
            music_label="WARNER MUSIC UK",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["POP-POP_ROCK"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["POP-POP_ROCK"].code),
            nb_galettes="1",
            performer="Gorillaz",
        ),
        idAtProviders="5054197199738",
        name="Cracker Island",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    available_rock_vinyl = offers_factories.ProductFactory(
        description='" The Hightlights " la compilation de ses plus grands tubes !\n\nAprès une année 2020 interstellaire ! The Weeknd nous livre ses plus grands HITS dans une compilation exceptionnelle !\n',
        extraData=offers_models.OfferExtraData(
            artist="The weeknd",
            author="The weeknd",
            date_parution=read_things_date("21/07/2023"),
            disponibility="Disponible",
            distributeur="Universal Music France",
            ean="0602435931975",
            editeur="UNIVERSAL",
            gtl_id="60200",
            music_label="RCA MUSIC GROUP/AMADE",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["ROCK-INDIE_ROCK"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["ROCK-INDIE_ROCK"].code),
            nb_galettes="1",
            performer="The Weeknd",
        ),
        idAtProviders="0602435931975",
        name="The Highlights",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    available_multiple_discs_vinyl = offers_factories.ProductFactory(
        description="LONDON GRAMMAR EST UN TRÈS JEUNE TRIO ANGLAIS FORMÉ SUR LES BANCS DE L'UNIVERSITÉ.\nAUTEURS-COMPOSITEURS-INTERPRÈTES : HANNAH REID, DOT MAJOR & DAN ROTHMAN SUSCITENT L'ENTHOUSIASME DE PART ET D'AUTRE DE LA MANCHE.\nPORTÉ PAR LA VOIX PUISSANTE ET BLUFFANTE DE HANNAH, LONDON GRAMMAR EST DÉJÀ CONSIDÉRÉ COMME LE PENDANT POP DE THE XX.",
        extraData=offers_models.OfferExtraData(
            artist="London grammar",
            author="London grammar",
            comment="édition double vinyle gatefold + CD",
            date_parution=read_things_date("02/01/2019"),
            disponibility="Disponible",
            distributeur="Universal Music France",
            ean="5060281614698",
            editeur="BECAUSE",
            gtl_id="60200",
            music_label="BECAUSE",
            musicSubType=str(MUSIC_SUB_TYPES_BY_SLUG["ROCK-INDIE_ROCK"].code),
            musicType=str(MUSIC_TYPES_BY_SLUG["ROCK-INDIE_ROCK"].code),
            nb_galettes="3",
            performer="London Grammar",
        ),
        idAtProviders="5060281614698",
        name="If you wait",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE.id,
    )

    return [
        unavailable_cd,
        soon_released_cd,
        available_rap_cd_1,
        available_rap_cd_2,
        available_multiple_discs_cd,
        available_french_cd,
        available_pop_vinyl_1,
        available_pop_vinyl_2,
        available_rock_vinyl,
        available_multiple_discs_vinyl,
    ]
