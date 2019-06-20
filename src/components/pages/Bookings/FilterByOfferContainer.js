import {compose} from 'redux'
import {requestData} from 'redux-saga-data'
import {connect} from 'react-redux'
import {withFrenchQueryRouter} from 'components/hocs'

import {FilterByOffer} from './FilterByOffer'
import selectOffers from './selectOffers'
import selectOffersByVenueId from './selectOffersByVenueId'


export const mapDispatchToProps = (dispatch) => ({
  loadOffers: () => {
    dispatch(requestData({
      apiPath: `/offers`,
      stateKey: 'offers',
      method: 'GET'
    }))
  },
  selectBookingsForOffers: (offerId) => {
    dispatch(
      {
        payload: offerId,
        type: 'BOOKING_SUMMARY_SELECT_OFFER',
      }
    )
  }
})

export const mapStateToProps = state => {

  const allOffersOption = {
    name: "Toutes les offres",
    id: "all",
  }

  const venueId = state.bookingSummary.selectedVenue
  const {isFilterByDigitalVenues}=state.bookingSummary

  let offersOptions = []

  if (isFilterByDigitalVenues){
    const digitalOffers = selectOffers(isFilterByDigitalVenues, state)
    offersOptions = [allOffersOption, ...digitalOffers]
  } else {
    if(venueId==="all"){
      const nonDigitalOffers = selectOffers(isFilterByDigitalVenues, state)
      offersOptions = [allOffersOption, ...nonDigitalOffers]
    } else {
      const offersWithSelectedVenueId = selectOffersByVenueId(venueId, state)
      offersOptions = [allOffersOption, ...offersWithSelectedVenueId]
    }
  }

  return {
    offersOptions,
    isFilterByDigitalVenues: state.bookingSummary.isFilterByDigitalVenues,
    offerId: state.bookingSummary.selectedOffer,
    venueId,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(FilterByOffer)
