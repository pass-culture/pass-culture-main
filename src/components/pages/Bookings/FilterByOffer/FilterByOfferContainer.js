import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import FilterByOffer from './FilterByOffer'
import { selectIsUserAdmin } from '../../../../selectors/data/usersSelectors'
import {
  selectDigitalOffers,
  selectOffersByVenueId,
} from '../../../../selectors/data/offersSelectors'
import { offerNormalizer } from '../../../../utils/normalizers'

const PAGINATION_LIMIT = 1000

export const mapDispatchToProps = dispatch => ({
  loadOffers: venueId => {
    let getOffersApiPath = `/offers?paginate=${PAGINATION_LIMIT}`
    if (venueId !== undefined && venueId !== 'all') {
      getOffersApiPath += `&venueId=${venueId}`
    }
    dispatch(
      requestData({
        apiPath: getOffersApiPath,
        method: 'GET',
        stateKey: 'offers',
        normalizer: offerNormalizer,
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
