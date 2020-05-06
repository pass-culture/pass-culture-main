from repository import repository
from sqlalchemy.sql.expression import func
from models import UserSQLEntity


def update_hasSeenTutorials_for_existing_users():
    print("[USERS UPDATE] START")
    users_to_update = UserSQLEntity.query\
        .filter(UserSQLEntity.email.like('%@%'))\
        .filter(func.length(UserSQLEntity.publicName) > 2)\
        .filter(UserSQLEntity.culturalSurveyFilledDate != None)\
        .all()

    for user in users_to_update:
        user.hasSeenTutorials = True

    repository.save(*users_to_update)
    print(f"{len(users_to_update)} USERS UPDATED")
    print("[USERS UPDATE] END")
