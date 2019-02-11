import get from 'lodash.get'
import { withLogin } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import offererSelector from '../../../selectors/offerer'
import selectUserOffererByOffererIdAndUserIdAndRightsType from '../../../selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'
import selectVenuePatchByVenueIdByOffererId from '../../../selectors/selectVenuePatchByVenueIdByOffererId'

import RawVenuePage from './RawVenuePage'

function mapStateToProps(state, ownProps) {
  const { offererId, venueId } = ownProps.match.params
  const { id: userId } = state.user || {}
  return {
    adminUserOfferer: selectUserOffererByOffererIdAndUserIdAndRightsType(
      state,
      offererId,
      userId,
      'admin'
    ),
    formGeo: get(state, 'form.venue.geo'),
    formLatitude: get(state, 'form.venue.latitude'),
    formLongitude: get(state, 'form.venue.longitude'),
    formSire: get(state, `form.venue.sire`),
    formSiret: get(state, 'form.venue.siret'),
    formComment: get(state, 'form.venue.comment'),
    name: get(state, `form.venue.name`),
    offerer: offererSelector(state, offererId),
    user: state.user,
    venuePatch: selectVenuePatchByVenueIdByOffererId(state, venueId, offererId),
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withRouter,
  connect(mapStateToProps)
)(RawVenuePage)
