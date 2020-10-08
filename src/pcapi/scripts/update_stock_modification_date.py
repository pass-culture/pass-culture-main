from pcapi.models.db import db


def update_stock_modification_date_sql_version():

    db.engine.execute(
        """
        BEGIN TRANSACTION;
        
        ALTER TABLE stock DISABLE TRIGGER stock_update;
        
        UPDATE stock
        SET "dateModified" = last_update_from_activity_table.last_update
        FROM (SELECT cast(old_data->> 'id' AS INT) as stock_id, MAX(issued_at) as last_update
        FROM activity
        WHERE table_name = 'stock' AND verb = 'update'
        GROUP BY stock_id
        ORDER BY last_update) as last_update_from_activity_table
        WHERE stock.id = last_update_from_activity_table.stock_id;
        
        ALTER TABLE stock ENABLE TRIGGER stock_update;
        
        COMMIT;
        """
    )
