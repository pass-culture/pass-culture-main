import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import FilterByOffer from './FilterByOffer'
import selectDigitalOffers from '../selectors/selectDigitalOffers'
import selectOffersByVenueId from '../selectors/selectOffersByVenueId'
import selectIsUserAdmin from '../selectors/selectIsUserAdmin'

export const mapDispatchToProps = dispatch => ({
  loadOffers: () => {
    dispatch(
      requestData({
        apiPath: `/offers`,
        method: 'GET',
        stateKey: 'offers',
      })
    )
  },
  updateOfferId: event => {
    dispatch({
      payload: event.target.value,
      type: 'BOOKING_SUMMARY_UPDATE_OFFER_ID',
    })
  },
})

export const mapStateToProps = state => {
  const isUserAdmin = selectIsUserAdmin(state)

  const { bookingSummary = {} } = state
  const { isFilteredByDigitalVenues, offerId, venueId } = bookingSummary

  const allOffersOption = {
    id: 'all',
    name: 'Toutes les offres',
  }

  let offersOptions = []

  if (!isUserAdmin) {
    if (isFilteredByDigitalVenues) {
      const digitalOffers = selectDigitalOffers(state)
      offersOptions = [allOffersOption, ...digitalOffers]
    } else {
      if (venueId === 'all') {
        offersOptions = []
      } else {
        const offersFromSpecificVenue = selectOffersByVenueId(state, venueId)
        offersOptions = [allOffersOption, ...offersFromSpecificVenue]
      }
    }
  }

  const showDateSection = offerId !== 'all' && !!offerId

  return {
    isFilteredByDigitalVenues,
    offerId,
    offersOptions,
    showDateSection,
    venueId,
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(FilterByOffer)
