import get from 'lodash.get'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'
import { showNotification } from 'pass-culture-shared'

import Mediation from './Mediation'
import { withRequiredLogin } from '../../hocs'
import selectMediationById from '../../../selectors/selectMediationById'
import selectOfferById from '../../../selectors/selectOfferById'
import selectOffererById from '../../../selectors/selectOffererById'
import selectVenueById from '../../../selectors/selectVenueById'

import { mediationNormalizer, offerNormalizer } from '../../../utils/normalizers'

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
    getOffer: offerId => {
      dispatch(
        requestData({
          apiPath: `/offers/${offerId}`,
          normalizer: offerNormalizer,
        })
      )
    },
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
    showFailDataNotification: error => {
      dispatch(
        showNotification({
          text: error,
          type: 'fail',
        })
      )
    },
    showSuccessDataNotification: () => {
      dispatch(
        showNotification({
          tag: 'mediations-manager',
          text: 'Votre accroche a bien été enregistrée',
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

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Mediation)
