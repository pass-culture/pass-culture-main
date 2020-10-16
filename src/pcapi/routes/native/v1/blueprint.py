from flask import Blueprint
from spectree import SpecTree

from pcapi.serialization.utils import before_handler


native_v1 = Blueprint('native_v1', __name__)

api = SpecTree("flask", MODE="strict", before=before_handler, PATH='/')
api.register(native_v1)
