from sqlalchemy import func

AND = '-'
LANGUAGE = 'french'

def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector(LANGUAGE, exp)

def get_ts_query(token):
    return token.strip().replace(' ', ' | ')


def get_ts_queries(search):
    if AND in search:
        tokens = [token for token in search.split('-') if token.strip() != '']
        return [get_ts_query(token) for token in tokens]
    return [get_ts_query(search)]
