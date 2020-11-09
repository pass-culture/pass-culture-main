from itertools import chain

from flask_login import current_user
from flask_login import login_required

from pcapi.flask_app import private_api
from pcapi.models.offerer import Offerer
from pcapi.repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from pcapi.routes.serialization.reimbursement_csv_serialize import find_all_offerer_reimbursement_details
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv


@private_api.route('/reimbursements/csv', methods=['GET'])
@login_required
def get_reimbursements_csv():
    query = filter_query_where_user_is_user_offerer_and_is_validated(
        Offerer.query,
        current_user
    )

    all_validated_offerers_for_the_current_user = query.all()

    reimbursement_details = chain(*[
        find_all_offerer_reimbursement_details(offerer.id)
        for offerer in all_validated_offerers_for_the_current_user
    ])

    reimbursement_details_csv = generate_reimbursement_details_csv(reimbursement_details)

    return reimbursement_details_csv.encode('utf-8-sig'), \
           200, \
           {'Content-type': 'text/csv; charset=utf-8;',
            'Content-Disposition': 'attachment; filename=remboursements_pass_culture.csv'}
