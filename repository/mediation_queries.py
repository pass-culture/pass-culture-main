from models import Mediation


def find_by_id(mediation_id):
    return Mediation.query.filter_by(id=mediation_id).first()


def get_all_tuto_mediations():
    return Mediation.query.filter(Mediation.tutoIndex != None) \
                          .order_by(Mediation.tutoIndex) \
                          .all()
