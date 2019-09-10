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
    stock_in_errors = []

    activities = db.engine.execute(query).fetchall()
    number_of_activities_done = 0

    print("Number of activities found: %s" % len(activities))

    for activity in activities:
        stock_id = activity[0]
        modified_date = activity[1]
        stock = Stock.query.get(stock_id)

        if stock is None:
            stocks_not_found.append(stock_id)
            continue

        stock.dateModified = modified_date

        try:
            PcObject.save(stock)
        except Exception:
            stock_in_errors.append(stock.id)

        number_of_activities_done += 1

        if number_of_activities_done % CHUNK_SIZE == 0:
            print("Number of stocks updated : %s" % number_of_activities_done)

    print("Number of stocks updated : %s" % number_of_activities_done)
    print(stock_in_errors)

# First try failed : [14, 13, 4624, 8622, 8623, 8624, 8626, 8628, 8631, 3441, 3442, 3443, 3444, 3445, 3446, 3447, 3448, 3449, 3450, 3451, 3452, 3453, 3454, 3455, 3456, 3457, 3458, 3459, 3460, 3461, 3462, 3463, 3464, 3465, 3466, 3467, 3468, 3469, 3470, 3471, 3472, 3473, 3474, 3475, 3476, 3477, 3478, 3479, 3480, 3481, 3482, 3483, 3484, 3485, 3486, 3487, 3488, 3489, 3490, 3491, 3492, 3493, 3494, 3495, 3496, 3497, 3498, 3499, 3500, 3501, 3502, 3503, 3504, 3505, 3506, 3507, 3508, 3509, 3510, 3511, 3512, 3513, 3514, 3515, 3516, 3517, 3518, 3519, 3520, 3521, 3522, 3523, 3524, 3525, 3526, 3527, 3528, 3529, 3530, 3531, 3532, 3533]
