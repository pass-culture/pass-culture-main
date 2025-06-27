import hashlib
import itertools
import logging

from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def ean_generator(factor: int) -> str:
    seed = 7236233859864
    return str((seed * (factor + 1)))[:13]


def allocine_id_generator(factor: int) -> str:
    seed = 7236233859864
    return str((seed * (factor + 1)))[:10]


def create_industrial_chronicles() -> None:
    logger.info("create_industrial_chronicles")
    users = (
        db.session.query(users_models.User)
        .filter(users_models.User.roles.contains([users_models.UserRole.BENEFICIARY]))
        .order_by(users_models.User.id)
        .limit(10)
    )

    for ean in (
        "9782073034809",
        "9782073094681",
        "9782203296619",
        "9782290415313",
        "9782413081715",
        "9791034770366",
        "9782731695014",
        "9782849535301",
        "9782253251491",
        "9791035208547",
    ):
        offers_factories.ProductFactory.create(ean=ean)

    products_with_ean = (
        db.session.query(offers_models.Product)
        .filter(
            ~offers_models.Product.ean.is_(None),
        )
        .order_by(offers_models.Product.id)
        .limit(9)
    )

    products_with_allocine_id = []
    for allocineId in (1000002449, 1000007194, 1000004644):
        products_with_allocine_id.append(offers_factories.ProductFactory.create(extraData={"allocineId": allocineId}))

    logger.info("Creating 'BOOK' type chronicles with all fields")
    for user, product, i in zip(itertools.cycle(users), itertools.cycle(products_with_ean), range(30)):
        ean = product.ean or "1234567890123"
        chronicles_factories.ChronicleFactory.create(
            age=(15 + (i % 5)),
            city=user.city,
            content=f"Chronique BOOK sur le produit {product.name} écrite par l'utilisateur {user.full_name} ({user.id}).",
            identifierChoiceId=hashlib.sha256(ean.encode()).hexdigest()[:20],
            productIdentifier=ean,
            productIdentifierType=chronicles_models.ChronicleProductIdentifierType.EAN,
            clubType=chronicles_models.ChronicleClubType.BOOK_CLUB,
            email=user.email,
            firstName=user.firstName,
            isActive=bool(i % 5 == 0),
            isIdentityDiffusible=bool(i % 2 == 0),
            isSocialMediaDiffusible=bool(i % 3 == 0),
            user=user,
            products=[product],
        )

    logger.info("Creating 'BOOK' type chronicles without user")
    for product, i in zip(itertools.cycle(products_with_ean), range(5)):
        ean = product.ean or "1234567890123"
        chronicles_factories.ChronicleFactory.create(
            age=(15 + (i % 5)),
            city=["Paris", None][i % 2],
            content=f"Chronique BOOK sur le produit {product.name} mais sans utilisateur.",
            identifierChoiceId=hashlib.sha256(ean.encode()).hexdigest()[:20],
            productIdentifier=ean,
            productIdentifierType=chronicles_models.ChronicleProductIdentifierType.EAN,
            clubType=chronicles_models.ChronicleClubType.BOOK_CLUB,
            email=f"emailnotfound{i}@example.com",
            isActive=bool(i % 5 == 0),
            isIdentityDiffusible=bool(i % 2 == 0),
            isSocialMediaDiffusible=bool(i % 3 == 0),
            products=[product],
        )

    logger.info("Creating 'BOOK' type chronicles without products")
    for user, i in zip(itertools.cycle(users), range(5)):
        ean = ean_generator(i)
        chronicles_factories.ChronicleFactory.create(
            age=(15 + (i % 5)),
            city=user.city,
            content=f"Chronique BOOK sans produit mais écrite par l'utilisateur {user.full_name} ({user.id}).",
            identifierChoiceId=hashlib.sha256(ean.encode()).hexdigest()[:20],
            productIdentifier=ean,
            productIdentifierType=chronicles_models.ChronicleProductIdentifierType.EAN,
            clubType=chronicles_models.ChronicleClubType.BOOK_CLUB,
            email=user.email,
            firstName=user.firstName,
            isActive=bool(i % 5 == 0),
            isIdentityDiffusible=bool(i % 2 == 0),
            isSocialMediaDiffusible=bool(i % 3 == 0),
            user=user,
        )

    logger.info("Création d'une chronique 'BOOK' minimale et une longue")
    chronicles_factories.ChronicleFactory.create(
        content="minimal chronicle",
        clubType=chronicles_models.ChronicleClubType.BOOK_CLUB,
    )
    chronicles_factories.ChronicleFactory.create(
        productIdentifier=ean_generator(123),
        productIdentifierType=chronicles_models.ChronicleProductIdentifierType.EAN,
        clubType=chronicles_models.ChronicleClubType.BOOK_CLUB,
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

    logger.info("Creating 'CINÉ' type chronicles with all fields")
    for user, product, i in zip(itertools.cycle(users), itertools.cycle(products_with_allocine_id), range(15)):
        allocine_id = str(product.extraData["allocineId"])
        chronicles_factories.ChronicleFactory.create(
            age=(20 + (i % 7)),
            content=f"Chronique CINÉ sur le produit {product.name} écrite par l'utilisateur {user.full_name} ({user.id}).",
            identifierChoiceId=hashlib.sha256(allocine_id.encode()).hexdigest()[:20],
            productIdentifier=allocine_id,
            productIdentifierType=chronicles_models.ChronicleProductIdentifierType.ALLOCINE_ID,
            clubType=chronicles_models.ChronicleClubType.CINE_CLUB,
            email=user.email,
            firstName=user.firstName,
            isActive=bool(i % 3 == 0),
            isIdentityDiffusible=bool(i % 2 == 0),
            isSocialMediaDiffusible=bool(i % 4 == 0),
            user=user,
            products=[product],
        )

    logger.info("Creating 'CINÉ' type chronicles without user")
    for product, i in zip(itertools.cycle(products_with_allocine_id), range(3)):
        allocine_id = str(product.extraData["allocineId"])
        chronicles_factories.ChronicleFactory.create(
            age=(20 + (i % 7)),
            content=f"Chronique CINÉ sur le produit {product.name} mais sans utilisateur.",
            identifierChoiceId=hashlib.sha256(allocine_id.encode()).hexdigest()[:20],
            productIdentifier=allocine_id,
            productIdentifierType=chronicles_models.ChronicleProductIdentifierType.ALLOCINE_ID,
            clubType=chronicles_models.ChronicleClubType.CINE_CLUB,
            email=f"cine_anon{i}@example.com",
            isActive=bool(i % 3 == 0),
            isIdentityDiffusible=bool(i % 2 == 0),
            isSocialMediaDiffusible=bool(i % 4 == 0),
            products=[product],
        )

    logger.info("Creating 'CINÉ' type chronicles without products")
    for user, i in zip(itertools.cycle(users), range(5)):
        allocine_id = allocine_id_generator(i)
        chronicles_factories.ChronicleFactory.create(
            age=(20 + (i % 7)),
            city=user.city,
            content=f"Chronique CINÉ sans produit mais écrite par l'utilisateur {user.full_name} ({user.id}).",
            identifierChoiceId=hashlib.sha256(allocine_id.encode()).hexdigest()[:20],
            productIdentifier=allocine_id,
            productIdentifierType=chronicles_models.ChronicleProductIdentifierType.ALLOCINE_ID,
            clubType=chronicles_models.ChronicleClubType.CINE_CLUB,
            email=user.email,
            firstName=user.firstName,
            isActive=bool(i % 3 == 0),
            isIdentityDiffusible=bool(i % 2 == 0),
            isSocialMediaDiffusible=bool(i % 4 == 0),
            user=user,
        )
