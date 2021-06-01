from sqlalchemy import func

from pcapi.models import db


def get_batches(query, key, batch_size):
    """Return a list of queries to process the requested query by batches.

    It supposes that keys are evenly spread (i.e there are no gaps of
    varying size). Otherwise it will work but the batches will not be
    of the same size, which may lead to the very performance issues
    you are trying to avoid.

    WARNING: if your initial query is ordered in DESCending order, the
    returned batch queries will NOT be ordered correctly. You will
    have to reverse the order of the returned iterator.
    """
    sub = query.subquery()
    min_key, max_key = db.session.query(func.min(sub.c.id), func.max(sub.c.id)).one()

    if (min_key, max_key) == (None, None):
        return

    ranges = [(i, i + batch_size - 1) for i in range(min_key, max_key + 1, batch_size)]
    for start, end in ranges:
        yield query.filter(key.between(start, end))
