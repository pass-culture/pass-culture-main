from typing import List

from models.db import db


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
        SET "dateCreated" = activity.issued_at
        FROM activity
        WHERE table_name='stock'
        AND (changed_data ->>'id')::int = stock.id
        AND verb='insert';
        '''
    db.engine.execute(query)


def populate_cultural_survey_filled_date_from_activity():
    query = f'''
        UPDATE "user"
        SET "culturalSurveyFilledDate" = activity.issued_at
        FROM activity
        WHERE table_name='user'
        AND (changed_data ->>'id')::int = "user".id
        AND (changed_data ->>'needsToFillCulturalSurvey')::bool = false
        AND verb='update';
        '''
    db.engine.execute(query)
