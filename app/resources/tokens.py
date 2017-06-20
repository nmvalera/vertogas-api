from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from flask_restful.utils.cors import crossdomain

from ..common import ALLOWED_CROSS_ORIGIN_DOMAIN, \
    VERTOGAS_URL_PREFIX, POWER_PLANTS_RESOURCE, TOKENS_RESOURCE, LOGS_RESOURCE, \
    DEFAULT_CONTRACT_ID
from ..extensions import db
from ..tokens.helpers import TokenHelpers
from ..tokens.serializers import token_schema_api, log_schema_api, power_plant_schema_api

# Make auth API
VERTOGAS_BLUEPRINT_NAME = 'vertogas'
vertogas_bp = Blueprint(VERTOGAS_BLUEPRINT_NAME, __name__, url_prefix=VERTOGAS_URL_PREFIX)
vertogas_api = Api(vertogas_bp)


class PowerPlantResource(Resource):
    """
    Resource responsible for returning cities in a given zone
    """
    @crossdomain(origin=ALLOWED_CROSS_ORIGIN_DOMAIN, credentials=True)
    def get(self, owner=None):
        token_helpers = TokenHelpers(db.session)
        power_plants = token_helpers.get_power_plants(DEFAULT_CONTRACT_ID, owner)
        return jsonify(power_plant_schema_api.dump(power_plants, many=True).data)

    # Handles pre-flight OPTIONS http request
    @crossdomain(origin=ALLOWED_CROSS_ORIGIN_DOMAIN, methods=['GET'], headers=['content-type'], credentials=True)
    def options(self):
        # When cross domain decorator is fired on OPTIONS http request a response is automatically sent
        # (change param automatic_options to False in order to call the function)
        pass


vertogas_api.add_resource(PowerPlantResource,
                          POWER_PLANTS_RESOURCE,
                          '%s/<string:owner>' % POWER_PLANTS_RESOURCE)


class TokenResource(Resource):
    """
    Resource responsible for returning cities in a given zone
    """
    @crossdomain(origin=ALLOWED_CROSS_ORIGIN_DOMAIN, credentials=True)
    def get(self, power_plant_id=None, owner=None):
        token_helpers = TokenHelpers(db.session)
        tokens = token_helpers.get_tokens(DEFAULT_CONTRACT_ID, power_plant_id=power_plant_id, owner=owner)
        return jsonify(token_schema_api.dump(tokens, many=True).data)

    # Handles pre-flight OPTIONS http request
    @crossdomain(origin=ALLOWED_CROSS_ORIGIN_DOMAIN, methods=['GET'], headers=['content-type'], credentials=True)
    def options(self):
        # When cross domain decorator is fired on OPTIONS http request a response is automatically sent
        # (change param automatic_options to False in order to call the function)
        pass


vertogas_api.add_resource(TokenResource,
                          '%s/power_plant/<int:power_plant_id>' % TOKENS_RESOURCE,
                          '%s/owner/<string:owner>' % TOKENS_RESOURCE)


class LogResource(Resource):
    """
    Resource responsible for returning cities in a given zone
    """
    @crossdomain(origin=ALLOWED_CROSS_ORIGIN_DOMAIN, credentials=True)
    def get(self, token_id):
        token_helpers = TokenHelpers(db.session)
        tokens = token_helpers.get_logs(DEFAULT_CONTRACT_ID, token_id)
        return jsonify(log_schema_api.dump(tokens, many=True).data)

    # Handles pre-flight OPTIONS http request
    @crossdomain(origin=ALLOWED_CROSS_ORIGIN_DOMAIN, methods=['GET'], headers=['content-type'], credentials=True)
    def options(self):
        # When cross domain decorator is fired on OPTIONS http request a response is automatically sent
        # (change param automatic_options to False in order to call the function)
        pass


vertogas_api.add_resource(LogResource, '%s/<int:token_id>' % LOGS_RESOURCE)
