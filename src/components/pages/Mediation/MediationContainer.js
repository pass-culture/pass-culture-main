import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { withRequiredLogin } from 'components/hocs'
import { selectOfferById } from 'store/offers/selectors'
import { loadOffer } from 'store/offers/thunks'
import { showNotificationV1 } from 'store/reducers/notificationReducer'
import { selectMediationById } from 'store/selectors/data/mediationsSelectors'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectVenueById } from 'store/selectors/data/venuesSelectors'
import { mediationNormalizer } from 'utils/normalizers'

import Mediation from './Mediation'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: {
      params: { mediationId, offerId },
    },
  } = ownProps
  const offer = selectOfferById(state, offerId)
  const venue = selectVenueById(state, get(offer, 'venueId'))
  return {
    offer,
    offerer: selectOffererById(state, get(venue, 'managingOffererId')),
    mediation: selectMediationById(state, mediationId),
  }
}

export const mapDispatchToProps = dispatch => {
  return {
    getMediation: (mediationId, handleSuccess, handleFail) => {
      dispatch(
        requestData({
          apiPath: `/mediations/${mediationId}`,
          handleSuccess,
          handleFail,
          normalizer: mediationNormalizer,
        })
      )
    },
    loadOffer: offerId => dispatch(loadOffer(offerId)),
    showOfferModificationErrorNotification: error => {
      dispatch(
        showNotificationV1({
          text: error,
          type: 'fail',
        })
      )
    },
    showOfferModificationValidationNotification: () => {
      dispatch(
        showNotificationV1({
          tag: 'mediations-manager',
          text:
            'Votre offre a bien été modifiée. Cette offre peut mettre quelques minutes pour être disponible dans l’application.',
          type: 'success',
        })
      )
    },
    createOrUpdateMediation: (isNew, mediation, body, handleFailData, handleSuccessData) => {
      dispatch(
        requestData({
          apiPath: `/mediations${isNew ? '' : `/${get(mediation, 'id')}`}`,
          body,
          encode: 'multipart/form-data',
          handleFail: handleFailData,
          handleSuccess: handleSuccessData,
          method: isNew ? 'POST' : 'PATCH',
          stateKey: 'mediations',
        })
      )
    },
  }
}

export default compose(withRequiredLogin, connect(mapStateToProps, mapDispatchToProps))(Mediation)
