import { closeNotification, lastTrackerMoment, showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { withRequiredLogin } from 'components/hocs'
import { SAVE_SEARCH_FILTERS } from 'store/reducers/offers'
import { selectOffers } from 'store/selectors/data/offersSelectors'
import { fetchFromApiWithCredentials } from 'utils/fetch'
import { ALL_OFFERS, ALL_VENUES } from './_constants'
import Offers from './Offers'

export const mapStateToProps = state => {
  return {
    lastTrackerMoment: lastTrackerMoment(state, 'offers'),
    notification: state.notification,
    offers: selectOffers(state),
    searchFilters: state.offers.searchFilters,
  }
}

const buildQueryParams = ({ nameSearchValue, selectedVenueId, page }) => {
  const queryParams = []

  if (nameSearchValue !== ALL_OFFERS) {
    queryParams.push(`name=${nameSearchValue}`)
  }

  if (selectedVenueId !== ALL_VENUES) {
    queryParams.push(`venueId=${selectedVenueId}`)
  }

  if (page) {
    queryParams.push(`page=${page}`)
  }

  return queryParams.join('&')
}

export const mapDispatchToProps = dispatch => {
  const showOffersActivationNotification = notificationMessage => {
    dispatch(
      showNotification({
        tag: 'offers-activation',
        text: notificationMessage,
        type: 'success',
      })
    )
  }
  return {
    closeNotification: () => dispatch(closeNotification()),

    handleOnActivateAllVenueOffersClick: venueId => () => {
      dispatch(
        requestData({
          apiPath: `/venues/${venueId}/offers/activate`,
          method: 'PUT',
          stateKey: 'offers',
          handleSuccess: showOffersActivationNotification(
            'Toutes les offres de ce lieu ont été activées avec succès'
          ),
        })
      )
    },

    handleOnDeactivateAllVenueOffersClick: venueId => () => {
      dispatch(
        requestData({
          apiPath: `/venues/${venueId}/offers/deactivate`,
          method: 'PUT',
          stateKey: 'offers',
          handleSuccess: showOffersActivationNotification(
            'Toutes les offres de ce lieu ont été désactivées avec succès'
          ),
        })
      )
    },

    saveSearchFilters: filters => {
      dispatch({
        type: SAVE_SEARCH_FILTERS,
        filters,
      })
    },

    loadOffers: filters =>
      fetchFromApiWithCredentials(`/offers?${buildQueryParams(filters)}`).then(
        ({ offers, page, page_count: pageCount, total_count: offersCount }) => {
          dispatch({
            type: 'GET_PAGINATED_OFFERS',
            payload: offers,
          })

          return { page, pageCount, offersCount }
        }
      ),
  }
}

export default compose(withRequiredLogin, connect(mapStateToProps, mapDispatchToProps))(Offers)
