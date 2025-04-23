import hashlib
import itertools
import logging

from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


def ean_generator(factor: int) -> str:
    seed = 7236233859864
    return str((seed * (factor + 1)))[:13]


def create_industrial_chronicles() -> None:
    logger.info("create_industrial_chronicles")
    users = (
        users_models.User.query.filter(users_models.User.roles.contains([users_models.UserRole.BENEFICIARY]))
        .order_by(users_models.User.id)
        .limit(10)
    )
    products = (
        offers_models.Product.query.filter(
            ~offers_models.Product.ean.is_(None),
        )
        .order_by(offers_models.Product.id)
        .limit(9)
    )

    logger.info("create chronicles with all fields")
    for user, product, i in zip(itertools.cycle(users), itertools.cycle(products), range(30)):
        ean = product.ean or "1234567890123"
        chronicles_factories.ChronicleFactory.create(
            age=(15 + (i % 5)),
            city=user.city,
            content=f"Chronique sur le produit {product.name} écrite par l'utilisateur {user.full_name} ({user.id}).",
            eanChoiceId=hashlib.sha256(ean.encode()).hexdigest()[:20],
            ean=ean,
            email=user.email,
            firstName=user.firstName,
            isActive=bool(i % 5 == 0),
            isIdentityDiffusible=bool(i % 2 == 0),
            isSocialMediaDiffusible=bool(i % 3 == 0),
            user=user,
            products=[product],
        )

    logger.info("create chronicles without user")
    for product, i in zip(itertools.cycle(products), range(5)):
        ean = product.ean or "1234567890123"
        chronicles_factories.ChronicleFactory.create(
            age=(15 + (i % 5)),
            city=["Paris", None][i % 2],
            content=f"Chronique sur le produit {product.name} mais sans utilisateur.",
            eanChoiceId=hashlib.sha256(ean.encode()).hexdigest()[:20],
            ean=ean,
            email=f"emailnotfound{i}@example.com",
            isActive=bool(i % 5 == 0),
            isIdentityDiffusible=bool(i % 2 == 0),
            isSocialMediaDiffusible=bool(i % 3 == 0),
            products=[product],
        )

    logger.info("create chronicles without products")
    for user, i in zip(itertools.cycle(users), range(5)):
        ean = ean_generator(i)
        chronicles_factories.ChronicleFactory.create(
            age=(15 + (i % 5)),
            city=user.city,
            content=f"Chronique sans produit mais écrite par l'utilisateur {user.full_name} ({user.id}).",
            eanChoiceId=hashlib.sha256(ean.encode()).hexdigest()[:20],
            ean=ean,
            email=user.email,
            firstName=user.firstName,
            isActive=bool(i % 5 == 0),
            isIdentityDiffusible=bool(i % 2 == 0),
            isSocialMediaDiffusible=bool(i % 3 == 0),
            user=user,
        )

    chronicles_factories.ChronicleFactory.create(
        content="minimal chronicle",
    )
    chronicles_factories.ChronicleFactory.create(
        ean=ean_generator(123),
        content="""
Une chronique avec un très long contenu en Français mais comme je n'ai pas d'idées voici à la place un extrait quelconque du Discours de la servitude volontaire d'Étienne de La Boétie:

    Enfin, si l’on voit non pas cent, non pas mille hommes, mais cent pays, mille villes, un million
d’hommes ne pas assaillir celui qui les traite tous comme autant de serfs et d’esclaves, comment
qualifierons-nous cela ? Est-ce lâcheté ? Mais tous les vices ont des bornes qu’ils ne peuvent pas
dépasser. Deux hommes, et même dix, peuvent bien en craindre un ; mais que mille, un million,
mille villes ne se défendent pas contre un seul homme, cela n’est pas couardise : elle ne va pas
jusque-là, de même que la vaillance n’exige pas qu’un seul homme escalade une forteresse, attaque
une armée, conquière un royaume. Quel vice monstrueux est donc celui-ci, qui ne mérite pas même
le titre de couardise, qui ne trouve pas de nom assez laid, que la nature désavoue et que la langue
refuse de nommer ?

    Qu’on mette face à face cinquante mille hommes en armes ; qu’on les range en bataille, qu’ils
en viennent aux mains ; les uns, libres, combattent pour leur liberté, les autres combattent pour la
leur ravir. Auxquels promettrez-vous la victoire ? Lesquels iront le plus courageusement au combat : ceux qui espèrent pour récompense le maintien de leur liberté, ou ceux qui n’attendent pour
salaire des coups qu’il donnent et qu’ils reçoivent que la servitude d’autrui ? Les uns ont toujours devant les yeux le bonheur de leur vie passée et l’attente d’un bien-être égal pour l’avenir.
Ils pensent moins à ce qu’ils endurent le temps d’une bataille qu’à ce qu’ils endureraient, vaincus, eux, leurs enfants et toute leur postérité. Les autres n’ont pour aiguillon qu’une petite pointe
de convoitise qui s’émousse soudain contre le danger, et dont l’ardeur s’éteint dans le sang de
leur première blessure. Aux batailles si renommées de Miltiade, de Léonidas, de Thémistocle, qui
datent de deux mille ans et qui vivent encore aujourd’hui aussi fraîches dans la mémoire des livres
et des hommes que si elles venaient d’être livrées hier, en Grèce, pour le bien des Grecs et pour
l’exemple du monde entier, qu’est-ce qui donna à un si petit nombre de Grecs, non pas le pouvoir,
mais le courage de supporter la force de tant de navires que la mer elle-même en débordait, de
vaincre des nations si nombreuses que tous les soldats grecs, pris ensemble, n’auraient pas fourni
assez de capitaines aux armées ennemies ? Dans ces journces glorieuses, c’était moins la bataille
des Grecs contre les Perses que la victoire de la liberté sur la domination, de l’affranchissement sur
la convoitise.
""",
    )
