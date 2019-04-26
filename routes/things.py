""" things """
import simplejson as json
from flask import current_app as app

from models import Product
from utils.rest import login_or_api_key_required, \
    handle_rest_get_list


# FIXME Pas de tests sur cette route, est-elle utilisée ?
@app.route('/things/<ofType>:<identifier>', methods=['GET'])
@login_or_api_key_required
def get_thing(ofType, identifier):
    query = Product.query.filter(
        (Product.type == ofType) &
        (Product.idAtProviders == identifier)
    )
    thing_product = query.first_or_404()
    return json.dumps(thing_product)

# FIXME Pas de tests sur cette route, est-elle utilisée ? Le retour change suite au réfacto !
@app.route('/things', methods=['GET'])
@login_or_api_key_required
def list_things():
    return handle_rest_get_list(Product)
