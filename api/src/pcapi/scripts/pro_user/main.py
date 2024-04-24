import datetime

from pcapi.scripts.pro_user.set_eligibility.make_user_eligible import make_users_eligible_orm


if __name__ == "__main__":
    import argparse

    from pcapi.flask_app import app

    parser = argparse.ArgumentParser(description="""Set eligibility to new pro interface for users""")

    parser.add_argument("--ids", type=str, default="", help="list des ids des utilisateurs")
    parser.add_argument("--eligibility_date", type=str, default="", help="date d'eligibilité")
    parser.add_argument("--phase", type=int, default=1, help="phase de lancement")
    args = parser.parse_args()
    ids = [int(i) for i in args.ids.split(",")]
    date_eligible = datetime.datetime.strptime(args.eligibility_date, "%d/%m/%Y %H:%M")
    print(date_eligible, ids, args.phase)
    with app.app_context():
        make_users_eligible_orm(ids, date_eligible, phase=args.phase)
