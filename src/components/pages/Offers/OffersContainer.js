import { closeNotification, lastTrackerMoment, showNotification } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import Offers from './Offers'
import { withRequiredLogin } from '../../hocs'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectVenueById } from 'store/selectors/data/venuesSelectors'
import { translateQueryParamsToApiParams } from '../../../utils/translate'
import { selectOffers } from 'store/selectors/data/offersSelectors'
import { fetchFromApiWithCredentials } from '../../../utils/fetch'
import { ALL_OFFERS, ALL_VENUES } from './_constants'

export const mapStateToProps = (state, ownProps) => {
  const { query } = ownProps
  const queryParams = query.parse()
  const apiQueryParams = translateQueryParamsToApiParams(queryParams)
  const { offererId, venueId } = apiQueryParams

  return {
    lastTrackerMoment: lastTrackerMoment(state, 'offers'),
    notification: state.notification,
    offers: selectOffers(state),
    offerer: selectOffererById(state, offererId),
    types: state.data.types,
    venue: selectVenueById(state, venueId),
  }
}

const buildQueryParams = ({ nameSearchValue, selectedVenue, page }) => {
  const queryParams = []

  if (nameSearchValue !== ALL_OFFERS) {
    queryParams.push(`name=${nameSearchValue}`)
  }

  if (selectedVenue !== ALL_VENUES) {
    queryParams.push(`venueId=${selectedVenue}`)
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

    handleOnActivateAllVenueOffersClick: venue => () => {
      dispatch(
        requestData({
          apiPath: `/venues/${venue.id}/offers/activate`,
          method: 'PUT',
          stateKey: 'offers',
          handleSuccess: showOffersActivationNotification(
            'Toutes les offres de ce lieu ont été activées avec succès'
          ),
        })
      )
    },

    handleOnDeactivateAllVenueOffersClick: venue => () => {
      dispatch(
        requestData({
          apiPath: `/venues/${venue.id}/offers/deactivate`,
          method: 'PUT',
          stateKey: 'offers',
          handleSuccess: showOffersActivationNotification(
            'Toutes les offres de ce lieu ont été désactivées avec succès'
          ),
        })
      )
    },

    loadOffers: (filters, handleSuccess, handleFail) => {
      fetchFromApiWithCredentials(`/offers?${buildQueryParams(filters)}`)
        .then(({ offers, page, page_count: pageCount }) => {
          dispatch({
            type: 'GET_PAGINATED_OFFERS',
            payload: offers,
          })

          handleSuccess(page, pageCount)
        })
        .catch(() => {
          handleFail()
        })
    },

    loadTypes: () => dispatch(requestData({ apiPath: '/types' })),
  }
}

export default compose(withRequiredLogin, connect(mapStateToProps, mapDispatchToProps))(Offers)
