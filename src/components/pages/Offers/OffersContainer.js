import { lastTrackerMoment } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import { saveSearchFilters, setSelectedOfferIds } from 'store/offers/actions'
import { selectOffers } from 'store/offers/selectors'
import {
  loadOffers,
  setAllVenueOffersActivate,
  setAllVenueOffersInactivate,
} from 'store/offers/thunks'
import { hideActionsBar, showActionsBar } from 'store/reducers/actionsBar'
import { closeNotification, showNotificationV1 } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { fetchFromApiWithCredentials } from 'utils/fetch'

import Offers from './Offers'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
    getOfferer: fetchOffererById,
    lastTrackerMoment: lastTrackerMoment(state, 'offers'),
    notification: state.notification,
    offers: selectOffers(state),
    savedSearchFilters: state.offers.searchFilters,
    selectedOfferIds: state.offers.selectedOfferIds,
  }
}

const fetchOffererById = offererId => fetchFromApiWithCredentials(`/offerers/${offererId}`)

export const mapDispatchToProps = dispatch => {
  const showOffersActivationNotification = notificationMessage => {
    dispatch(
      showNotificationV1({
        tag: 'offers-activation',
        text: notificationMessage,
        type: 'success',
      })
    )
  }
  return {
    closeNotification: () => dispatch(closeNotification()),
    handleOnActivateAllVenueOffersClick: venueId => () => {
      dispatch(setAllVenueOffersActivate(venueId)).then(() => {
        showOffersActivationNotification(
          'Toutes les offres de ce lieu ont été activées avec succès'
        )
      })
    },
    handleOnDeactivateAllVenueOffersClick: venueId => () => {
      dispatch(setAllVenueOffersInactivate(venueId)).then(() => {
        showOffersActivationNotification(
          'Toutes les offres de ce lieu ont été désactivées avec succès'
        )
      })
    },
    hideActionsBar: () => dispatch(hideActionsBar()),
    loadOffers: filters => dispatch(loadOffers(filters)),
    saveSearchFilters: filters => dispatch(saveSearchFilters(filters)),
    setSelectedOfferIds: selectedOfferIds => dispatch(setSelectedOfferIds(selectedOfferIds)),
    showActionsBar: () => dispatch(showActionsBar()),
  }
}

export default compose(withQueryRouter(), connect(mapStateToProps, mapDispatchToProps))(Offers)
