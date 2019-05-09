from itertools import chain
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.reimbursement import generate_reimbursements_csv
from models.offerer import Offerer
from repository.reimbursement_queries import find_all_offerer_reimbursements
from repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated

@app.route('/reimbursements/csv', methods=['GET'])
@login_required
def get_reimbursements_csv():
    query = filter_query_where_user_is_user_offerer_and_is_validated(Offerer.query,
                                                                     current_user)

    reimbursements = chain(*list(map(lambda o: find_all_offerer_reimbursements(o.id),
                               query)))

    reimbursements_csv = generate_reimbursements_csv(reimbursements)

    return reimbursements_csv.encode('utf-8-sig'), \
           200, \
           {'Content-type': 'text/csv; charset=utf-8;',
            'Content-Disposition': 'attachment; filename=reservations_pass_culture.csv'}
