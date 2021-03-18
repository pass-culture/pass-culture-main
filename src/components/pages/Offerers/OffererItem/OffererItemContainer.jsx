import { connect } from 'react-redux'

import { isAPISireneAvailable, selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'
import {
  selectPhysicalVenuesByOffererId,
  selectVenuesByOffererId,
} from 'store/selectors/data/venuesSelectors'

import OffererItem from './OffererItem'

export const mapStateToProps = (state, ownProps) => {
  const {
    offerer: { id: offererId },
  } = ownProps
  return {
    isNewHomepageActive: selectIsFeatureActive(state, 'PRO_HOMEPAGE'),
    isVenueCreationAvailable: isAPISireneAvailable(state),
    physicalVenues: selectPhysicalVenuesByOffererId(state, offererId),
    venues: selectVenuesByOffererId(state, offererId),
  }
}

export default connect(mapStateToProps)(OffererItem)
