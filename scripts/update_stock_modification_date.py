from models.db import db

CHUNK_SIZE = 500


def update_stock_modification_date_sql_version():

    # FIXME Should we disable activity trigger, to avoid to add entries ?
    # ALTER TABLE stock DISABLE TRIGGER audit_trigger_update;
    # ALTER TABLE stock ENABLE TRIGGER audit_trigger_update;

    db.engine.execute(
        """
        BEGIN TRANSACTION;
        
        ALTER TABLE stock DISABLE TRIGGER stock_update;
        
        UPDATE stock
        SET "dateModified" = last_udpate_from_activity_table.last_update
        FROM (SELECT cast(old_data->> 'id' AS INT) as stock_id, MAX(issued_at) as last_update
        FROM activity
        WHERE table_name = 'stock' AND verb = 'update'
        GROUP BY stock_id
        ORDER BY last_update) as last_udpate_from_activity_table
        WHERE stock.id = last_udpate_from_activity_table.stock_id;
        
        ALTER TABLE stock ENABLE TRIGGER stock_update;
        
        COMMIT;
        """
    )

# First try failed : [14, 13, 4624, 8622, 8623, 8624, 8626, 8628, 8631, 3441, 3442, 3443, 3444, 3445, 3446, 3447, 3448, 3449, 3450, 3451, 3452, 3453, 3454, 3455, 3456, 3457, 3458, 3459, 3460, 3461, 3462, 3463, 3464, 3465, 3466, 3467, 3468, 3469, 3470, 3471, 3472, 3473, 3474, 3475, 3476, 3477, 3478, 3479, 3480, 3481, 3482, 3483, 3484, 3485, 3486, 3487, 3488, 3489, 3490, 3491, 3492, 3493, 3494, 3495, 3496, 3497, 3498, 3499, 3500, 3501, 3502, 3503, 3504, 3505, 3506, 3507, 3508, 3509, 3510, 3511, 3512, 3513, 3514, 3515, 3516, 3517, 3518, 3519, 3520, 3521, 3522, 3523, 3524, 3525, 3526, 3527, 3528, 3529, 3530, 3531, 3532, 3533]
