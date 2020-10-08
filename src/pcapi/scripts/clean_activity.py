from typing import List

from pcapi.models.db import db


def delete_tables_from_activity(tables: List[str]):
    tables_with_quotes = [f"'{table}'" for table in tables]
    tables_as_str = ', '.join(tables_with_quotes)
    query = f"""
        DELETE FROM activity WHERE table_name IN ({tables_as_str})
    """
    db.engine.execute(query)


def populate_stock_date_created_from_activity():
    query = f'''
        UPDATE stock
        SET "dateCreated" = all_stocks.dateCreated
        FROM (
            SELECT 
            DISTINCT ON (stock_id)
            (activity.changed_data ->>'id')::int AS stock_id,
            activity.issued_at AS dateCreated
            FROM activity
            WHERE table_name='stock'
            AND verb='insert'
        ) AS all_stocks
        WHERE all_stocks.stock_id = stock.id;
        '''
    db.engine.execute(query)


def populate_cultural_survey_filled_date_from_activity():
    query = f'''
        UPDATE "user"
        SET "culturalSurveyFilledDate" = typeform.filling_date
        FROM (
            SELECT 
            DISTINCT ON (user_id)
            (activity.old_data ->>'id')::int AS user_id,
            activity.issued_at AS filling_date
            FROM activity
            WHERE table_name='user'
            AND (changed_data ->>'needsToFillCulturalSurvey')::bool = false
            AND verb='update'
            ORDER BY user_id, filling_date DESC            
        ) AS typeform
        WHERE typeform.user_id = "user".id;
        '''
    db.engine.execute(query)




