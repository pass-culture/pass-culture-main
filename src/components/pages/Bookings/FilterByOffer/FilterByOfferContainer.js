import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'

import { FilterByOffer } from './FilterByOffer'
import selectOffers from '../selectors/selectOffers'
import selectOffersByVenueId from '../selectors/selectOffersByVenueId'

export const mapDispatchToProps = dispatch => ({
  loadOffers: () => {
    dispatch(
      requestData({
        apiPath: `/offers`,
        stateKey: 'offers',
        method: 'GET',
      })
    )
  },
  selectBookingsForOffers: event => {
    dispatch({
      payload: event.target.value,
      type: 'BOOKING_SUMMARY_SELECT_OFFER',
    })
  },
})

export const mapStateToProps = state => {
  const { bookingSummary = {} } = state
  const { isFilterByDigitalVenues, selectedOffer, selectedVenue } = bookingSummary

  const allOffersOption = {
    name: 'Toutes les offres',
    id: 'all',
  }

  let offersOptions

  if (isFilterByDigitalVenues) {
    const isDigital = true
    const digitalOffers = selectOffers(state, isDigital)
    offersOptions = [allOffersOption, ...digitalOffers]
  } else {
    if (selectedVenue === 'all') {
      const isDigital = false
      const allOffers = selectOffers(state, isDigital)
      offersOptions = [allOffersOption, ...allOffers]
    } else {
      const offersFromSpecificVenue = selectOffersByVenueId(state, selectedVenue)
      offersOptions = [allOffersOption, ...offersFromSpecificVenue]
    }
  }

  const showDateSection = selectedOffer !== 'all' && !!selectedOffer

  return {
    isFilterByDigitalVenues,
    offerId: state.bookingSummary.selectedOffer,
    offersOptions,
    selectedVenue: state.bookingSummary.selectedVenue,
    showDateSection,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(FilterByOffer)
