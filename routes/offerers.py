""" offerers """
from base64 import b64decode
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from utils.human_ids import dehumanize, humanize
from utils.object_storage import store_public_object
from utils.rest import handle_rest_get_list, login_or_api_key_required

Offerer = app.model.Offerer
UserOfferer = app.model.UserOfferer
RightsType = app.model.RightsType
User = app.model.User


def check_offerer_user(query):
    return query.filter(Offerer.users.any(User.id == current_user.id))\
                .first_or_404()


offerer_include = [
# TODO
#    {'key': 'providers',
#     'sub_joins': ['-apiKey',
#                   '-apiKeyGenerationDate']
#    }
]


@app.route('/offerers', methods=['GET'])
@login_required
def list_offerers():
    return handle_rest_get_list(Offerer,
                                include=offerer_include)


@app.route('/offerers/<offererId>', methods=['GET'])
@login_required
def get_offerer(offererId):
    query = Offerer.query.filter_by(id=dehumanize(offererId))\
                         .first_or_404()
    check_offerer_user(query)
    return jsonify(query._asdict(include=offerer_include))


@app.route('/offerers', methods=['POST'])
@login_or_api_key_required
def create_offerer():
    offerer = Offerer(from_dict=request.json)
    if current_user:
        user_offerer = UserOfferer()
        user_offerer.offerer = offerer
        user_offerer.user = current_user
        user_offerer.rights = RightsType.admin
        app.db.session.add(user_offerer)

    app.model.PcObject.check_and_save(offerer)

    if 'thumb_content' in request.json:
        store_public_object(
            "thumbs",
            "offerers/"+humanize(offerer.id),
            b64decode(request.json['thumb_content']),
            request.json['thumb_content_type']
        )
    return jsonify(offerer._asdict()), 201
