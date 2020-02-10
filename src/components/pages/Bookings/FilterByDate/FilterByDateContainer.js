import { compose } from 'redux'
import { connect } from 'react-redux'
import { withFrenchQueryRouter } from '../../../hocs'

import FilterByDate from './FilterByDate'
import { selectStocksByOfferId } from '../../../../selectors/data/stocksSelectors'
import { selectOfferById } from '../../../../selectors/data/offersSelectors'
import { selectVenueById } from '../../../../selectors/data/venuesSelectors'
import { getTimezoneFromDepartementCode } from '../../Offer/StocksManager/StockItem/utils/utils'

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
  let timezone = 'Europe/Paris'

  if (offerId && offerId !== 'all') {
    const offer = selectOfferById(state, offerId)

    if (offer.isThing) {
      showThingDateSection = true
    }

    if (offer.isEvent) {
      const venue = selectVenueById(state, venueId)
      if (!venue.isVirtual) {
        timezone = getTimezoneFromDepartementCode(venue.departementCode)
      }
      stocks = selectStocksByOfferId(state, offerId)
      showEventDateSection = true
    }
  }

  return {
    showEventDateSection,
    showThingDateSection,
    stocks,
    timezone,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(FilterByDate)
