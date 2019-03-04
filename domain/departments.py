from typing import List

from models import User

DEPARTEMENT_CODE_VISIBILITY = {'93': ['75', '77', '78', '91', '92', '93', '94', '95'],
                        '29': ['22', '25', '29', '56'],
                        '67': ['54', '55', '57', '67', '68', '88'],
                        '34': ['11', '12', '30', '34', '48', '81'],
                        '97': ['97', '971', '972', '973']}
ILE_DE_FRANCE_DEPT_CODES = ['75', '78', '91', '94', '93', '95']


def get_departement_codes_from_user(user: User) -> List[str]:
    if user.departementCode[:2] in DEPARTEMENT_CODE_VISIBILITY:
        return DEPARTEMENT_CODE_VISIBILITY[user.departementCode[:2]]
    else:
        return [user.departementCode]