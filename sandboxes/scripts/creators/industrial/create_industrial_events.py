from domain.types import get_formatted_event_or_thing_types
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_event

MOCK_NAMES = [
    "Nekfeu versus Lordon",
    "Punk sous un cathodique",
    "This is Spartaaaaa",
    "C'est notre prooooojecteur",
    "La commune sans guillemin",
    "Avez-vous déjà vu ?"
]

MOCK_DESCRIPTIONS = [
    "Nous ne voyons pas les choses mêmes ; nous nous bornons, le plus souvent, à lire des étiquettes collées sur elles. Cette tendance, issue du besoin, s'est encore accentuée sous l'influence du langage. Car les mots (à l'exception des noms propres) désignent des genres. Le mot, qui ne note de la chose que sa fonction la plus commune et son aspect banal, s'insinue entre elle et nous.",
    "Et ce ne sont pas seulement les objets extérieurs, ce sont aussi nos propres états d'âme qui se dérobent à nous dans ce qu'ils ont d'intime, de personnel, d'originalement vécu. Quand nous éprouvons de l'amour ou de la haine, quand nous nous sentons joyeux ou tristes, est-ce bien notre sentiment lui-même qui arrive à notre conscience avec les mille nuances fugitives et les mille résonances profondes qui en font quelque chose d'absolument nôtre ?",
    "Nous serions alors tous romanciers, tous poètes, tous musiciens. Mais, le plus souvent, nous n'apercevons de notre état d'âme que son déploiement extérieur. Nous ne saisissons de nos sentiments que leur aspect impersonnel, celui que le langage a pu noter une fois pour toutes parce qu'il est à peu près le même dans les mêmes conditions, pour tous les hommes.",
    "Ainsi, jusque dans notre propre individu, l'individualité nous échappe. Nous nous mouvons parmi des généralités et des symboles, comme en un champ clos où notre force se mesure utilement avec d'autres forces ; et, fascinés par l'action, attirés par elle, pour notre plus grand bien, sur le terrain qu'elle s'est choisie, nous vivons dans une zone mitoyenne entre les choses et nous, extérieurement aux choses, extérieurement aussi à nous-mêmes.",
    "Quant à l'espèce de spectacles, c'est nécessairement le plaisir qu'ils donnent et non leur utilité qui la détermine. Si l'utilité peut s'y trouver, à la bonne heure ; mais l'objet principal est de plaire, et pourvu que le peuple s'amuse, cet objet est assez rempli. Cela seul empêchera toujours qu'on ne puisse donner à ces sortes d'établissements tous les avantages dont ils seraient susceptibles, et c'est abuser beaucoup que de s'en former une idée de perfection qu'on ne saurait mettre en pratique sans rebuter ceux qu'on croit instruire.",
    "Voilà d'où naît la diversité des spectacles, selon les goûts divers des nations. Un peuple intrépide, grave et cruel, veut des fêtes meurtrières et périlleuses, où brillent la valeur et le sang-froid. Un peuple féroce et bouillant veut du sang, des combats et des passions atroces. Un peuple voluptueux veut de la musique et des danses. Un peuple galant veut de l'amour et de la politesse. Un peuple badin veut de la plaisanterie et du ridicule. Trahit sua quemque voluptas . Il faut, pour leur plaire, des spectacles qui favorisent leurs penchants, au lieu qu'il en faudrait qui les modérassent."
]

def create_industrial_events():
    logger.info('create_industrial_events')

    events_by_name = {}

    event_types = [t for t in get_formatted_event_or_thing_types() if t['type'] == 'Event']

    mock_index = -1

    for event_type in event_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
        mock_index += 1
        if mock_index > len(MOCK_NAMES) - 1:
            mock_index = 0

        events_by_name["{} / {}".format(event_type['value'], MOCK_NAMES[mock_index])] = create_event(
            description=MOCK_DESCRIPTIONS[mock_index],
            event_name=MOCK_NAMES[mock_index],
            event_type=event_type['value'],
            duration_minutes=60
        )

    PcObject.check_and_save(*events_by_name.values())

    return events_by_name
