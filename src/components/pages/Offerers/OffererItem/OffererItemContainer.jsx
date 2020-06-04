import { connect } from 'react-redux'

import OffererItem from './OffererItem'
import {
  selectPhysicalVenuesByOffererId,
  selectVenuesByOffererId,
} from '../../../../selectors/data/venuesSelectors'

import selectIsFeatureActive from '../../../router/selectors/selectIsFeatureActive'

export const mapStateToProps = (state, ownProps) => {
  const {
    offerer: { id: offererId },
  } = ownProps
  return {
    isVenueCreationAvailable: selectIsFeatureActive(state, 'API_SIRENE_AVAILABLE'),
    physicalVenues: selectPhysicalVenuesByOffererId(state, offererId),
    venues: selectVenuesByOffererId(state, offererId),
  }
}

export default connect(mapStateToProps)(OffererItem)
