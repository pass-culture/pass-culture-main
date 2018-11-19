from domain.types import get_formatted_event_or_thing_types_by_value
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_thing

MOCK_NAMES = [
    "Nez à Nez d'Anaconda",
    "Sous les parapluies de Borneo",
    "D-- tu l'auras",
    "Funky Family",
    "Sun aux lentilles",
    "Topaz de Reackham le Rouge"
]

MOCK_AUTHOR_NAMES = [
    "Simon Enclume",
    "Albert Mousquetaire",
    "Léa Duchamp",
    "Martine Marx",
    "Camille Forêt",
    "Robert Herbert"
]

MOCK_DESCRIPTIONS = [
    "Nous pourrions bien évidemment encourager ces méditations, soutenant que nous aimons toujours à l'échelle de notre sphère le bien-être d'entendre nos amis revenir d'expériences de mondes différents ; ou de raconter nous-mêmes son bonheur d'avoir goûté à l'échange simple des choses entre les Hommes d'un troquet, de se troquer des histoires comme on se cuisine ensemble la nourriture un soir d'été, de rentrer en transe sur une mélodie à trois notes, de tenter d'expliquer ce qui est beau du laid pour des enfants jouant dans une prairie encore verte, et enfin d'avoir pu chacun écouter le battement des blés mûrs entourant des chênes tout aussi dorés de soleil.",
    "Quoi! ne faut-il donc aucun Spectacle dans une République ? Au contraire, il en faut beaucoup. C'est dans les Républiques qu'ils sont nés, c'est dans leur sein qu'on les voit briller avec un véritable air de fête. A quels peuples convient-il mieux de s'assembler souvent et de former entre eux les doux liens du plaisir et de la joie, qu'à ceux qui ont tant de raisons de s'aimer et de rester à jamais unis ? Nous avons déjà plusieurs de ces fêtes publiques ; ayons-en, davantage encore, je n'en serai que plus charmée.",
    "Mais n'adoptons point ces Spectacles exclusifs qui renferment tristement un petit nombre de gens dans un antre obscur ; qui les tiennent craintifs et immobiles dans le silence et l'inaction ; qui n'offrent aux yeux que cloisons, que pointes de fer, que soldats, qu'affligeantes images de la servitude et de l'inégalité. Non, Peuples heureux, ce ne sont pas 1à vos fêtes !",
    "C'est en plein air, c'est sous le ciel qu'il faut vous rassembler et vous livrer au doux sentiment de votre bonheur. Que vos plaisirs ne soient, efféminées ni mercenaires, que rien de ce qui sent la contrainte et l'intérêt ne les empoisonne, qu'ils soient libres et généreux comme vous ; que le soleil éclaire vos innocents Spectacles ; vous en formerez un vous-mêmes, le plus digne qu'il puisse éclairer.",
    "Mais quels seront enfin les objets de ces Spectacles ? Qu'y montrera-t-on ? Rien, si l'on veut. Avec la liberté, partout où règne l'affluence, le bien-être y règne aussi. Plantez au milieu d'une place un piquet couronnée de fleurs, rassemblez-y le Peuple, et vous aurez une fête. Faites mieux encore : donnez les spectateurs en spectacle ; rendez-les acteurs eux-mêmes ; faites que chacun se voye et s'aime dans les autres, afin que tous en soient mieux unis.",
    "Chaque peuple veut des pièces qui lui ressemblent, et toute société n'a donc que les spectacles qu'elle mérite"
]

def create_industrial_things():
    logger.info('create_industrial_things')

    things_by_name = {}

    types_by_value = get_formatted_event_or_thing_types_by_value()

    thing_types = [t for t in types_by_value.values() if t['type'] == 'Thing']

    for (thing_index, thing_type) in enumerate(thing_types):

        mock_index = thing_index % len(MOCK_NAMES)

        name = "{} / {}".format(thing_type['value'], MOCK_NAMES[mock_index])
        things_by_name[name] = create_thing(
            is_national=True,
            author_name=MOCK_AUTHOR_NAMES[mock_index],
            description=MOCK_DESCRIPTIONS[mock_index],
            is_national=True if types_by_value[thing_type['value']]['onlineOnly'] else False,
            thing_name=MOCK_NAMES[mock_index],
            thing_type=thing_type['value'],
            url='https://ilestencoretemps.fr/'
            if types_by_value[thing_type['value']]['onlineOnly']
            else None)

    PcObject.check_and_save(*things_by_name.values())

    logger.info('created {} things'.format(len(things_by_name)))

    return things_by_name
