from models import Mediation


def get_all_tuto_mediations():
    return Mediation.query.filter(Mediation.tutoIndex != None) \
                          .order_by(Mediation.tutoIndex) \
                          .all()
