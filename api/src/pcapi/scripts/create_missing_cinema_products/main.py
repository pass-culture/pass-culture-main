"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/tcoudray-pass/PC-36884-chore-script-add-missing-products/api/src/pcapi/scripts/create_missing_cinema_products/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

# as we are using atomic
app.app_context().push()


_MOVIE_PRODUCTS_TO_CREATE: list[offers_models.Movie] = [
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=317519.html
    offers_models.Movie(
        allocine_id="317519",
        visa="151738",
        title="Un monde merveilleux",
        description="Dans un futur un peu trop proche où les humains dépendent des robots, Max, une ancienne prof réfractaire à la technologie, vivote avec sa fille grâce à des petites combines. Elle a un plan : kidnapper un robot dernier cri pour le revendre en pièces détachées. Mais tout dérape. Flanquée de ce robot qui l’exaspère, elle s’embarque dans une course-poursuite pour retrouver sa fille et prouver qu’il reste un peu d’humanité dans ce monde.",
        poster_url="https://fr.web.img6.acsta.net/c_310_420/img/8d/2b/8d2b0f843200159b6b3a2bb54d3e311c.jpg",
        duration=None,
        extra_data={
            "allocineId": 317519,
            "posterUrl": "https://fr.web.img6.acsta.net/c_310_420/img/8d/2b/8d2b0f843200159b6b3a2bb54d3e311c.jpg",
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=297804.html
    offers_models.Movie(
        allocine_id="297804",
        visa=None,
        title="L’Ame : une force dans sa vie",
        description="Depuis toujours, l’humanité s’interroge sur l’âme. Ce film propose de poursuivre cette réflexion en donnant la parole à des philosophes, des médecins, des thérapeutes, des chercheurs de sens, qui essaient de comprendre ce qu'est l'âme et comment elle peut être, plus que jamais, une ressource et une force dans la vie de chacun.",
        poster_url="https://fr.web.img3.acsta.net/c_310_420/pictures/22/02/10/16/32/5951235.jpg",
        duration=None,
        extra_data={
            "allocineId": 297804,
            "posterUrl": "https://fr.web.img3.acsta.net/c_310_420/pictures/22/02/10/16/32/5951235.jpg",
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=1000001994.html
    offers_models.Movie(
        allocine_id="1000001994",
        visa=None,
        title="La Couleur de l'esclavage",
        description="Entre le XVIe et le XIXe siècle, 25 000 convois d’environ 300 à 450 captifs Africains, traversèrent l’Atlantique après 40 à 50 jours de périple vers les Antilles. Plus d’un million d’entre eux perdirent la vie. Ainsi pour répondre au besoin de main-d’œuvre, dans ses colonies, l’Europe a déporté plus de 14 millions de captifs de diverses nations Africaines ; dans le seul but de les exploiter dans des plantations. Nous voilà au cœur de l’esclavage colonial.",
        poster_url="https://fr.web.img6.acsta.net/c_310_420/img/17/9e/179e8ad5531f344d4f2c6170fb49ad20.jpg",
        duration=None,
        extra_data={
            "allocineId": 1000001994,
            "posterUrl": "https://fr.web.img6.acsta.net/c_310_420/img/17/9e/179e8ad5531f344d4f2c6170fb49ad20.jpg",
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=236155.html
    offers_models.Movie(
        allocine_id="236155",
        visa="143562",
        title="Le Garçon et la Bête",
        description="Shibuya, le monde des humains, et Jutengai, le monde des Bêtes... C'est l'histoire d'un garçon solitaire et d'une Bête seule, qui vivent chacun dans deux mondes séparés. Un jour, le garçon se perd dans le monde des Bêtes où il devient le disciple de la Bête Kumatetsu qui lui donne le nom de Kyuta. Cette rencontre fortuite est le début d'une aventure qui dépasse l'imaginaire...",
        poster_url="https://fr.web.img6.acsta.net/c_310_420/pictures/15/10/06/14/28/553693.jpg",
        duration=None,
        extra_data={
            "allocineId": 236155,
            "posterUrl": "https://fr.web.img6.acsta.net/c_310_420/pictures/15/10/06/14/28/553693.jpg",
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=4223.html
    offers_models.Movie(
        allocine_id="4223",
        visa=None,
        title="Notes pour Debussy",
        description="Aout 1966: Jean-Luc Godard tourne Deux ou trois choses que je sais d'elle avec Marina Vlady dans la cite des 4 000 a La Courneuve. Dix ans plus tard on assiste en direct a la television a la destruction par implosion de la barre Debussy un des immeubles de ce grand ensemble. Entre ces deux dates, sous forme d'une lettre ouverte a Jean-Luc Godard, le film retrace la vie de cette cite.",
        poster_url=None,
        duration=None,
        extra_data={
            "allocineId": 4223,
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=1000025723.html
    offers_models.Movie(
        allocine_id="1000025723",
        visa=None,
        title="Rap-En-Aubrac",
        description="Sur le plateau de l’Aubrac en Aveyron, de jeunes adolescents bien intrigués par la nouveauté proposée en cette rentrée,  décident de s’inscrire à des ateliers de rap pendant une année. C’est le rappeur Kohndo qui sera leur professeur. Même si tous n’ont pas la même facilité à se lancer, l’artiste a bien l’intention de réussir à tous les faire rapper d’ici l’été. Au rythmes des saisons, ils se mettent à clamer ce qu’ils ont sur le coeur : leurs galères, leurs colères et leurs rêves d’un monde meilleur. Ce conte documentaire et musical raconte leurs histoires de rap en Aubrac.",
        poster_url="https://fr.web.img3.acsta.net/c_310_420/img/d4/f7/d4f7e06e877eb46943fce021b786633e.jpg",
        duration=None,
        extra_data={
            "allocineId": 1000025723,
            "posterUrl": "https://fr.web.img3.acsta.net/c_310_420/img/d4/f7/d4f7e06e877eb46943fce021b786633e.jpg",
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=190796.html
    offers_models.Movie(
        allocine_id="190796",
        visa="108270",
        title="Le tableau",
        description="Un château, des jardins fleuris, une forêt menaçante, voilà ce qu’un Peintre, pour des raisons mystérieuses, a laissé inachevé. Dans ce tableau vivent trois sortes de personnages : les Toupins qui sont entièrement peints, les Pafinis auxquels il manque quelques couleurs et les Reufs qui ne sont que des esquisses. S'estimant supérieurs, les Toupins prennent le pouvoir, chassent les Pafinis du château et asservissent les Reufs. Persuadés que seul le Peintre peut ramener l’harmonie en finissant le tableau, Ramo, Lola et Plume décident de partir à sa recherche. Au fil de l’aventure, les questions vont se succéder : qu'est devenu le Peintre ? Pourquoi les a t-il abandonnés ? Pourquoi a-t-il commencé à détruire certaines de ses toiles ! Connaîtront-ils un jour le secret du Peintre ?",
        poster_url="https://fr.web.img4.acsta.net/c_310_420/medias/nmedia/18/85/82/10/19840159.jpg",
        duration=None,
        extra_data={
            "allocineId": 190796,
            "posterUrl": "https://fr.web.img4.acsta.net/c_310_420/medias/nmedia/18/85/82/10/19840159.jpg",
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=55760.html
    offers_models.Movie(
        allocine_id="55760",
        visa=None,
        title="Salut à toi ",
        description="C'est l'histoire de deux groupes de musique, Les Hurlements de Léo et Les Ogres de Barback, qui ont fusionné le temps d'un projet commun: Un Air, Deux Familles.Ce groupe a été créé sans avoir la vocation de perdurer, juste le temps de parcourir les routes d'Europe sous les chapiteaux Latcho Drom.Trois ans de projet et plusieurs mois de concerts plus tard, ce film présente l'aventure humaine qu'a représentée cette tournée.",
        poster_url="https://fr.web.img6.acsta.net/c_310_420/medias/nmedia/18/71/53/13/19137278.jpg",
        duration=None,
        extra_data={
            "allocineId": 55760,
            "posterUrl": "https://fr.web.img6.acsta.net/c_310_420/medias/nmedia/18/71/53/13/19137278.jpg",
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=221524.html
    offers_models.Movie(
        allocine_id="221524",
        visa="142953",
        title="Seul sur Mars",
        description="Lors d’une expédition sur Mars, l’astronaute Mark Watney (Matt Damon) est laissé pour mort par ses coéquipiers, une tempête les ayant obligés à décoller en urgence. Mais Mark a survécu et il est désormais seul, sans moyen de repartir, sur une planète hostile. Il va devoir faire appel à son intelligence et son ingéniosité pour tenter de survivre et trouver un moyen de contacter la Terre. A 225 millions de kilomètres, la NASA et des scientifiques du monde entier travaillent sans relâche pour le sauver, pendant que ses coéquipiers tentent d’organiser une mission pour le récupérer au péril de leurs vies.",
        poster_url="https://fr.web.img6.acsta.net/c_310_420/pictures/15/09/08/15/20/305329.jpg",
        duration=None,
        extra_data={
            "allocineId": 221524,
            "posterUrl": "https://fr.web.img6.acsta.net/c_310_420/pictures/15/09/08/15/20/305329.jpg",
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=1000012394.html
    offers_models.Movie(
        allocine_id="1000012394",
        visa=None,
        title="Thesis on a Domestication",
        description="Une actrice transgenre à succès et son mari avocat décident d'adopter un enfant, défiant ainsi la communauté conservatrice d'Argentine.",
        poster_url=None,
        duration=None,
        extra_data={
            "allocineId": 1000012394,
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=306989.html
    offers_models.Movie(
        allocine_id="306989",
        visa=None,
        title="The People's Joker",
        description="Un clown en herbe aux prises avec son identité sexuelle combat un fasciste...",
        poster_url="https://fr.web.img6.acsta.net/c_310_420/pictures/24/03/07/11/02/2101802.jpg",
        duration=None,
        extra_data={
            "allocineId": 306989,
            "posterUrl": "https://fr.web.img6.acsta.net/c_310_420/pictures/24/03/07/11/02/2101802.jpg",
        },
    ),
    # https://www.allocine.fr/film/fichefilm_gen_cfilm=111135.html
    offers_models.Movie(
        allocine_id="111135",
        visa=None,
        title="Fandango",
        description="Au Pays Basque, José et Paul mènent une vie heureuse et paisible. José est remarqué pour sa jolie voix par le directeur d'un cabaret, qui lui propose de connaître la gloire. Il va devoir choisir entre mener sa carrière ou rester auprès de son ami et de celle qui l'aime, Angelica.",
        poster_url=None,
        duration=None,
        extra_data={
            "allocineId": 111135,
        },
    ),
]


def main(not_dry: bool = True) -> None:
    with atomic():
        provider = db.session.query(providers_models.Provider).filter_by(id=22)

        for movie in _MOVIE_PRODUCTS_TO_CREATE:
            product = offers_api.upsert_movie_product_from_provider(
                movie,
                provider,
                id_at_providers=f"{provider.id}:{movie.allocine_id}",
            )
            if product:  # mypy does not know that we will have a product
                logger.info("Product was successfully upserted", extra={"id": product.id, "name": product.name})

        if not_dry:
            # to rollback
            mark_transaction_as_invalid()
            logger.info("Finished dry run, rollback")

    if not not_dry:
        logger.info("Finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)
