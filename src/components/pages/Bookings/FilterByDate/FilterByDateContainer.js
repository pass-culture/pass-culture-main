import { compose } from 'redux'
import { connect } from 'react-redux'
import { withFrenchQueryRouter } from '../../../hocs'

import { FilterByDate } from './FilterByDate'
import selectStocksByOfferId from '../../../../selectors/selectStocksByOfferId'
import selectOfferById from '../../../../selectors/selectOfferById'

export const mapDispatchToProps = dispatch => ({
  selectBookingsDateFrom: date => {
    dispatch({
      payload: date,
      type: 'BOOKING_SUMMARY_SELECT_DATE_FROM',
    })
  },
  selectBookingsDateTo: date => {
    dispatch({
      payload: date,
      type: 'BOOKING_SUMMARY_SELECT_DATE_TO',
    })
  },
})

export const mapStateToProps = state => {
  const { bookingSummary = {} } = state
  const { selectedOffer } = bookingSummary

  let stocksOptions = []
  let showEventDateSection = false
  let showThingDateSection = false
  if (selectedOffer && selectedOffer !== 'all') {
    stocksOptions = selectStocksByOfferId(state, selectedOffer)
    const offer = selectOfferById(state, selectedOffer)
    showEventDateSection = offer.isEvent
    showThingDateSection = offer.isThing
  }

  return {
    selectBookingsDateFrom: state.bookingSummary.selectBookingsDateFrom,
    selectBookingsDateTo: state.bookingSummary.selectBookingsDateTo,
    showEventDateSection,
    showThingDateSection,
    stocksOptions,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(FilterByDate)
