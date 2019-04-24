import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Venue from './Venue'
import { withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'
import selectOffererById from 'selectors/selectOffererById'
import selectUserOffererByOffererIdAndUserIdAndRightsType from 'selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'
import selectVenuePatchByVenueIdByOffererId from 'selectors/selectVenuePatchByVenueIdByOffererId'

export const mapStateToProps = (state, ownProps) => {
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
    formSiret: get(state, 'form.venue.siret'),
    name: get(state, `form.venue.name`),
    offerer: selectOffererById(state, offererId),
    venuePatch: selectVenuePatchByVenueIdByOffererId(state, venueId, offererId),
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withRouter,
  connect(mapStateToProps)
)(Venue)
