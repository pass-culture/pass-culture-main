""" venues """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required
from os import path, environ
from pathlib import Path
import subprocess

from models.api_errors import ApiErrors
from utils.human_ids import dehumanize
from utils.includes import VENUE_PROVIDER_INCLUDES
from utils.rest import delete, expect_json_data,\
                       ensure_current_user_has_rights,\
                       load_or_404, update

VenueProvider = app.model.VenueProvider


@app.route('/venueProviders', methods=['GET'])
@login_required
def list_venue_providers():
    venueId = request.args.get('venueId')
    if venueId is None:
        e = ApiErrors()
        e.addError('venueId', 'Vous devez obligatoirement fournir le paramètre venueId')
        return jsonify(e.errors), 400

    vp_query = VenueProvider.query\
                            .filter_by(venueId=dehumanize(venueId))
    return jsonify([
        vp._asdict(include=VENUE_PROVIDER_INCLUDES)
        for vp in vp_query.all()
    ])


@app.route('/venueProviders/<id>', methods=['GET'])
@login_required
def get_venue_provider(id):
    vp = load_or_404(VenueProvider, id)
    return jsonify(vp._asdict(include=VENUE_PROVIDER_INCLUDES))


@app.route('/venueProviders', methods=['POST'])
@login_required
@expect_json_data
def create_venue_provider():
    new_vp = VenueProvider(from_dict=request.json)
    #TODO: check that provider is active
    app.model.PcObject.check_and_save(new_vp)
    api_root = Path(path.dirname(path.realpath(__file__))) / '..'
    p = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                         + ' --venueProvider ' + str(new_vp.id),
                         #stdout=subprocess.PIPE,
                         #stderr=subprocess.PIPE,
                         shell=True,
                         cwd=api_root)
    #out, err = p.communicate()
    #print("STDOUT:", out)
    #print("STDERR:", err)
    return jsonify(new_vp._asdict(include=VENUE_PROVIDER_INCLUDES)), 201


@app.route('/venueProviders/<id>', methods=['PATCH'])
@expect_json_data
def edit_venue_provider(id):
    vp = load_or_404(VenueProvider, id)
    update(vp, request.json)
    app.model.PcObject.check_and_save(vp)
    return jsonify(vp._asdict()), 200


@app.route('/venueProviders/<id>', methods=['DELETE'])
@login_required
def delete_venue_provider(id):
    vp = load_or_404(VenueProvider, id)
    ensure_current_user_has_rights(app.model.RightsType.editor,
                                   vp.venue.managingOffererId)
    # TODO: should we also delete all the associated events/things...?
    return delete(vp)
