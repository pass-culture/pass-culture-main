import get from 'lodash.get'

import selectOffererById from 'selectors/selectOffererById'
import selectUserOffererByOffererIdAndUserIdAndRightsType from 'selectors/selectUserOffererByOffererIdAndUserIdAndRightsType'
import selectPhysicalVenuesByOffererId from 'selectors/selectPhysicalVenuesByOffererId'

const mapStateToProps = (state, ownProps) => {
  const { currentUser, match } = ownProps
  const {
    params: { offererId },
  } = match
  const { id: currentUserId } = currentUser || {}

  return {
    adminUserOfferer: selectUserOffererByOffererIdAndUserIdAndRightsType(
      state,
      offererId,
      currentUserId,
      'admin'
    ),
    offerer: selectOffererById(state, offererId),
    offererName: get(state, 'form.offerer.name'),
    venues: selectPhysicalVenuesByOffererId(state, offererId),
  }
}

export default mapStateToProps
