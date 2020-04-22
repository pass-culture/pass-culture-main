from repository import repository
from models import User


def update_hasSeenTutorials_for_existing_users():
    print("[USERS UPDATE] START")
    users_to_update = User.query\
        .filter(User.culturalSurveyFilledDate != None)\
        .all()

    for user in users_to_update:
        user.hasSeenTutorials = True

    repository.save(*users_to_update)
    print(f"{len(users_to_update)} USERS UPDATED")
    print("[USERS UPDATE] END")
