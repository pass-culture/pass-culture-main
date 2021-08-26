/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'

import { isAPISireneAvailable } from 'store/features/selectors'
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
    isVenueCreationAvailable: isAPISireneAvailable(state),
    physicalVenues: selectPhysicalVenuesByOffererId(state, offererId),
    venues: selectVenuesByOffererId(state, offererId),
  }
}

export default connect(mapStateToProps)(OffererItem)
