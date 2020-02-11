import { compose } from 'redux'
import { connect } from 'react-redux'
import { withFrenchQueryRouter } from '../../../hocs'

import FilterByDate from './FilterByDate'
import { selectStocksByOfferId } from '../../../../selectors/data/stocksSelectors'
import { selectOfferById } from '../../../../selectors/data/offersSelectors'
import { selectVenueById } from '../../../../selectors/data/venuesSelectors'

export const mapDispatchToProps = dispatch => ({
  updateBookingsFrom: date => {
    dispatch({
      payload: date,
      type: 'BOOKING_SUMMARY_UPDATE_BOOKINGS_FROM',
    })
  },
  updateBookingsTo: date => {
    dispatch({
      payload: date,
      type: 'BOOKING_SUMMARY_UPDATE_BOOKINGS_TO',
    })
  },
})

export const mapStateToProps = state => {
  const { bookingSummary = {} } = state
  const { offerId, venueId } = bookingSummary

  let stocks = []
  let showEventDateSection = false
  let showThingDateSection = false
  let departementCode = '75'

  if (offerId && offerId !== 'all') {
    const offer = selectOfferById(state, offerId)

    if (offer.isThing) {
      showThingDateSection = true
    }

    if (offer.isEvent) {
      const venue = selectVenueById(state, venueId)
      departementCode = venue.departementCode
      stocks = selectStocksByOfferId(state, offerId)
      showEventDateSection = true
    }
  }

  return {
    departementCode,
    showEventDateSection,
    showThingDateSection,
    stocks,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(FilterByDate)
