import datetime

from pcapi.core.categories import subcategories_v2
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.repository import repository


def create_complex_offers(offerers_by_name: dict[str, offerers_models.Offerer]) -> None:
    offerers_iterator = iter(offerers_by_name.values())
    movie_product = offers_factories.ProductFactory(
        subcategoryId=subcategories_v2.SEANCE_CINE.id,
        name="good_cine_product",
        description="""
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur sed mi consectetur, sodales dolor ut, sollicitudin justo. Duis bibendum ligula luctus, sodales nunc at, lobortis arcu. In malesuada magna et magna sagittis, sit amet posuere nunc condimentum. Integer commodo dictum mi, at pellentesque dui. Nam vitae sollicitudin elit. Nullam interdum felis nisi, quis maximus ipsum volutpat sit amet. Duis commodo dolor quis dolor gravida imperdiet.

In in neque commodo, mattis ligula ac, laoreet dolor. Morbi interdum posuere lectus. Nam eu massa sapien. Proin faucibus, nisl eu ultricies tincidunt, metus lectus sodales ipsum, non maximus odio dui eu magna. Proin tristique lectus in nisl feugiat posuere. Praesent sit amet varius dolor, ut iaculis nulla. Suspendisse vel placerat ipsum. Nullam maximus sapien eros, ut tempus magna pharetra sed. Donec rutrum ipsum a commodo blandit. Pellentesque viverra, erat vitae lobortis tempus, augue quam convallis ante, sit amet malesuada ante eros eu augue. Etiam rutrum tellus et est commodo ullamcorper.
Ut quis egestas neque. Fusce sem nulla, luctus ac sagittis eu, mattis quis purus. Proin at pulvinar nisl.
        """,
        extraData={
            "cast": [
                "first actor",
                "second actor",
                "third actor",
            ],
            "type": "FEATURE_FILM",
            "visa": "123456",
            "genres": [
                "ADVENTURE",
                "ANIMATION",
                "DRAMA",
            ],
            "theater": {
                "allocine_room_id": "W1234",
                "allocine_movie_id": 654321,
            },
            "companies": [
                {
                    "company": {
                        "name": "Company1 Name",
                    },
                    "activity": "InternationalDistributionExports",
                },
                {
                    "company": {
                        "name": "Company2 Name",
                    },
                    "activity": "Distribution",
                },
                {
                    "company": {
                        "name": "Company3 Name",
                    },
                    "activity": "Production",
                },
                {
                    "company": {"name": "Company4 Name"},
                    "activity": "Production",
                },
                {
                    "company": {"name": "Company5 Name"},
                    "activity": "PrAgency",
                },
            ],
            "countries": [
                "Never Land",
            ],
            "releaseDate": "2023-04-12",
            "stageDirector": "John dupont",
            "diffusionVersion": "VO",
        },
    )

    movie_offer = offers_factories.OfferFactory(
        venue=next(offerers_iterator).managedVenues[0],
        name="good movie",
        subcategoryId=subcategories_v2.SEANCE_CINE.id,
        durationMinutes=133,
        description="""
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur sed mi consectetur, sodales dolor ut, sollicitudin justo. Duis bibendum ligula luctus, sodales nunc at, lobortis arcu. In malesuada magna et magna sagittis, sit amet posuere nunc condimentum. Integer commodo dictum mi, at pellentesque dui. Nam vitae sollicitudin elit. Nullam interdum felis nisi, quis maximus ipsum volutpat sit amet. Duis commodo dolor quis dolor gravida imperdiet.

In in neque commodo, mattis ligula ac, laoreet dolor. Morbi interdum posuere lectus. Nam eu massa sapien. Proin faucibus, nisl eu ultricies tincidunt, metus lectus sodales ipsum, non maximus odio dui eu magna. Proin tristique lectus in nisl feugiat posuere. Praesent sit amet varius dolor, ut iaculis nulla. Suspendisse vel placerat ipsum. Nullam maximus sapien eros, ut tempus magna pharetra sed. Donec rutrum ipsum a commodo blandit. Pellentesque viverra, erat vitae lobortis tempus, augue quam convallis ante, sit amet malesuada ante eros eu augue. Etiam rutrum tellus et est commodo ullamcorper.
Ut quis egestas neque. Fusce sem nulla, luctus ac sagittis eu, mattis quis purus. Proin at pulvinar nisl.
        """,
        idAtProvider="pouet provider",
        product=movie_product,
        isActive=True,
        isDuo=False,
        extraData={
            "cast": [
                "first actor",
                "second actor",
                "third actor",
            ],
            "type": "FEATURE_FILM",
            "visa": "123456",
            "genres": [
                "ADVENTURE",
                "ANIMATION",
                "DRAMA",
            ],
            "theater": {
                "allocine_room_id": "W1234",
                "allocine_movie_id": 654321,
            },
            "companies": [
                {
                    "company": {
                        "name": "Company1 Name",
                    },
                    "activity": "InternationalDistributionExports",
                },
                {
                    "company": {
                        "name": "Company2 Name",
                    },
                    "activity": "Distribution",
                },
                {
                    "company": {
                        "name": "Company3 Name",
                    },
                    "activity": "Production",
                },
                {
                    "company": {"name": "Company4 Name"},
                    "activity": "Production",
                },
                {
                    "company": {"name": "Company5 Name"},
                    "activity": "PrAgency",
                },
            ],
            "countries": [
                "Never Land",
            ],
            "releaseDate": "2023-04-12",
            "stageDirector": "Georges Méliès",
            "diffusionVersion": "VO",
        },
    )
    movie_stock = offers_factories.StockFactory(offer=movie_offer, bookingLimitDatetime=datetime.datetime.utcnow())
    repository.save(movie_stock)

    book_product = offers_factories.ProductFactory(
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        name="good book",
        description="""
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur sed mi consectetur, sodales dolor ut, sollicitudin justo. Duis bibendum ligula luctus, sodales nunc at, lobortis arcu. In malesuada magna et magna sagittis, sit amet posuere nunc condimentum. Integer commodo dictum mi, at pellentesque dui. Nam vitae sollicitudin elit. Nullam interdum felis nisi, quis maximus ipsum volutpat sit amet. Duis commodo dolor quis dolor gravida imperdiet.

In in neque commodo, mattis ligula ac, laoreet dolor. Morbi interdum posuere lectus. Nam eu massa sapien. Proin faucibus, nisl eu ultricies tincidunt, metus lectus sodales ipsum, non maximus odio dui eu magna. Proin tristique lectus in nisl feugiat posuere. Praesent sit amet varius dolor, ut iaculis nulla. Suspendisse vel placerat ipsum. Nullam maximus sapien eros, ut tempus magna pharetra sed. Donec rutrum ipsum a commodo blandit. Pellentesque viverra, erat vitae lobortis tempus, augue quam convallis ante, sit amet malesuada ante eros eu augue. Etiam rutrum tellus et est commodo ullamcorper.
Ut quis egestas neque. Fusce sem nulla, luctus ac sagittis eu, mattis quis purus. Proin at pulvinar nisl.
        """,
        extraData={
            "ean": "1234567891234",
            "dewey": "839",
            "rayon": "Littérature française Romans Nouvelles Correspondance",
            "author": "Étienne de La Boétie",
            "csr_id": "0101",
            "gtl_id": "01010000",
            "editeur": "Editor",
            "code_clil": "3442",
            "bookFormat": None,
            "collection": "Litterature",
            "prix_livre": "12.30",
            "distributeur": "Distributor",
            "date_parution": "12/12/1574",
            "titelive_regroup": "7138665",
            "num_in_collection": "0",
        },
    )

    book_offer = offers_factories.OfferFactory(
        venue=next(offerers_iterator).managedVenues[0],
        name="good book",
        subcategoryId=subcategories_v2.LIVRE_PAPIER.id,
        withdrawalDetails="demander a la caisse",
        description="""
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur sed mi consectetur, sodales dolor ut, sollicitudin justo. Duis bibendum ligula luctus, sodales nunc at, lobortis arcu. In malesuada magna et magna sagittis, sit amet posuere nunc condimentum. Integer commodo dictum mi, at pellentesque dui. Nam vitae sollicitudin elit. Nullam interdum felis nisi, quis maximus ipsum volutpat sit amet. Duis commodo dolor quis dolor gravida imperdiet.

In in neque commodo, mattis ligula ac, laoreet dolor. Morbi interdum posuere lectus. Nam eu massa sapien. Proin faucibus, nisl eu ultricies tincidunt, metus lectus sodales ipsum, non maximus odio dui eu magna. Proin tristique lectus in nisl feugiat posuere. Praesent sit amet varius dolor, ut iaculis nulla. Suspendisse vel placerat ipsum. Nullam maximus sapien eros, ut tempus magna pharetra sed. Donec rutrum ipsum a commodo blandit. Pellentesque viverra, erat vitae lobortis tempus, augue quam convallis ante, sit amet malesuada ante eros eu augue. Etiam rutrum tellus et est commodo ullamcorper.
Ut quis egestas neque. Fusce sem nulla, luctus ac sagittis eu, mattis quis purus. Proin at pulvinar nisl.
        """,
        idAtProvider="pouet provider",
        product=book_product,
        isActive=True,
        isDuo=False,
        extraData={
            "ean": "1234567891234",
            "dewey": "839",
            "rayon": "Littérature française Romans Nouvelles Correspondance",
            "author": "Étienne de La Boétie",
            "csr_id": "0101",
            "gtl_id": "01010000",
            "editeur": "Editor",
            "code_clil": "3442",
            "bookFormat": None,
            "collection": "Litterature",
            "prix_livre": "12.30",
            "distributeur": "Distributor",
            "date_parution": "12/12/1574",
            "titelive_regroup": "7138665",
            "num_in_collection": "0",
        },
    )
    offers_factories.StockFactory(offer=book_offer)

    electro_cd_offer = offers_factories.ThingOfferFactory(
        venue=next(offerers_iterator).managedVenues[0],
        name="Un super CD d'électro",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        extraData={"gtl_id": "04000000"},
    )
    offers_factories.StockFactory(offer=electro_cd_offer)

    classical_cd_offer = offers_factories.ThingOfferFactory(
        venue=next(offerers_iterator).managedVenues[0],
        name="Un CD de musique classique incroyable",
        subcategoryId=subcategories_v2.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        extraData={"gtl_id": "01000000"},
    )
    offers_factories.StockFactory(offer=classical_cd_offer)

    electro_event_offer = offers_factories.EventOfferFactory(
        venue=next(offerers_iterator).managedVenues[0],
        name="Un concert d'electro inoubliable",
        subcategoryId=subcategories_v2.CONCERT.id,
        extraData={"gtl_id": "04000000"},
    )
    offers_factories.StockFactory(offer=electro_event_offer)

    rock_event_offer = offers_factories.EventOfferFactory(
        venue=next(offerers_iterator).managedVenues[0],
        name="Un concert de rock un peu nul",
        subcategoryId=subcategories_v2.CONCERT.id,
        extraData={"gtl_id": "06000000"},
    )
    offers_factories.StockFactory(offer=rock_event_offer)
