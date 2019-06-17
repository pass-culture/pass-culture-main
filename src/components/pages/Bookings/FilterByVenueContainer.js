import {compose} from 'redux'
import {connect} from 'react-redux'
import { withFrenchQueryRouter } from 'components/hocs'

import selectOffersByVenueId from './selectOffersByVenueId'
import {FilterByVenue} from './FilterByVenue'

export const mapStateToProps = (state) => {
  //const { isDigital, venueId } = state.data
  const isDigital = true
  const venueId = "A8NA"
  console.log("isDigital", isDigital)
  console.log("venueId", venueId)
  const offers = selectOffersByVenueId(state, venueId)
  return {
    isDigital,
    offers,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(FilterByVenue)
