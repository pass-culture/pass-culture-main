from flask import current_app as app
from flask import render_template
from flask_login import login_required, current_user

from models.api_errors import ForbiddenError
from repository.okr_queries import get_beneficiary_users_details


@app.route('/dashboard/', methods=['GET'])
@login_required
def show_okr_page():
    if not current_user.isAdmin:
        raise ForbiddenError()
    return render_template('dashboard/home_page.html')


@app.route('/dashboard/users', methods=['GET'])
@login_required
def get_users_stats():
    if not current_user.isAdmin:
        raise ForbiddenError()
    beneficiary_users_details = get_beneficiary_users_details()
    return beneficiary_users_details.to_csv(), \
           200, \
           {'Content-type': 'text/csv; charset=utf-8;',
            'Content-Disposition': 'attachment; filename=reservations_pass_culture.csv'}
