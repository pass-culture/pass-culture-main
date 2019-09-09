from models import PcObject, Stock
from models.db import db

CHUNK_SIZE = 500


def update_stock_modification_date():
    query = """
    SELECT cast(old_data->> 'id' AS INT) as stock_id, MAX(issued_at) as last_update
    FROM activity
    WHERE table_name = 'stock' AND verb = 'update'
    GROUP BY stock_id
    ORDER BY last_update;
    """

    stocks_not_found = []
    stock_batch = []

    activities = db.engine.execute(query).fetchall()

    for activity in activities:
        stock_id = activity[0]
        modified_date = activity[1]
        stock = Stock.query.get(stock_id)

        if stock is None:
            stocks_not_found.append(stock_id)
            continue

        stock.dateModified = modified_date

        stock_batch.append(stock)

        if len(stock_batch) >= CHUNK_SIZE:
            PcObject.save(*stock_batch)
            stock_batch = []

    PcObject.save(*stock_batch)
