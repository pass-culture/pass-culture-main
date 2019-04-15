import get from 'lodash.get'

import selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity from './selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity'
import selectOffererById from 'selectors/selectOffererById'
import selectUserOffererByOffererIdAndUserIdAndRightsType from 'selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'

function mapStateToProps(state, ownProps) {
  const {
    currentUser,
    match: {
      params: { offererId, venueId },
    },
    query,
  } = ownProps
  const { id: currentUserId } = currentUser || {}
  const { isCreatedEntity } = query.context()

  const formInitialValues = selectFormInitialValuesByVenueIdAndOffererIdAndIsCreatedEntity(
    state,
    venueId,
    offererId,
    isCreatedEntity
  )

  return {
    adminUserOfferer: selectUserOffererByOffererIdAndUserIdAndRightsType(
      state,
      offererId,
      currentUserId,
      'admin'
    ),
    formInitialValues,
    formGeo: get(state, 'form.venue.geo'),
    formLatitude: get(state, 'form.venue.latitude'),
    formLongitude: get(state, 'form.venue.longitude'),
    formSire: get(state, `form.venue.sire`),
    formSiret: get(state, 'form.venue.siret'),
    formComment: get(state, 'form.venue.comment'),
    offerer: selectOffererById(state, offererId),
  }
}

export default mapStateToProps
