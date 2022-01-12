from dataclasses import asdict
from flask import Blueprint
from dowsingrod.app import limiter, rod


mod = Blueprint('api', __name__, url_prefix='/api')

@mod.route('/random')
@limiter.limit('2 per hour')
def random():
    treasure = rod.find_treasure()

    return asdict(treasure)

@mod.route('/current')
def current():
    # TODO: implement
    pass

