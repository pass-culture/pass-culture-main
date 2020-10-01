import { connect } from 'react-redux'

import OffererItem from './OffererItem'
import {
  selectPhysicalVenuesByOffererId,
  selectVenuesByOffererId,
} from 'store/selectors/data/venuesSelectors'

import { isAPISireneAvailable } from 'store/selectors/data/featuresSelectors'

export const mapStateToProps = (state, ownProps) => {
  const {
    offerer: { id: offererId },
  } = ownProps
  return {
    isVenueCreationAvailable: isAPISireneAvailable(state),
    physicalVenues: selectPhysicalVenuesByOffererId(state, offererId),
    venues: selectVenuesByOffererId(state, offererId),
  }
}

export default connect(mapStateToProps)(OffererItem)
