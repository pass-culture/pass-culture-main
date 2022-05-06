from pcapi.connectors.dms import models as dms_models


FINAL_INSTRUCTOR_DECISION_STATES = [
    dms_models.GraphQLApplicationStates.accepted,
    dms_models.GraphQLApplicationStates.refused,
]
