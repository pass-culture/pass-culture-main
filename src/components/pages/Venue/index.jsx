import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs'
import offererSelector from '../../../selectors/offerer'
import selectUserOffererByOffererIdAndUserIdAndRightsType from '../../../selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'
import selectVenuePatchByVenueIdByOffererId from '../../../selectors/selectVenuePatchByVenueIdByOffererId'

import RawVenue from './RawVenue'

function mapStateToProps(state, ownProps) {
  const { currentUser, match } = ownProps
  const {
    params: { offererId, venueId },
  } = match
  const { id: currentUserId } = currentUser || {}

  return {
    adminUserOfferer: selectUserOffererByOffererIdAndUserIdAndRightsType(
      state,
      offererId,
      currentUserId,
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
    venuePatch: selectVenuePatchByVenueIdByOffererId(state, venueId, offererId),
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withRouter,
  connect(mapStateToProps)
)(RawVenue)
