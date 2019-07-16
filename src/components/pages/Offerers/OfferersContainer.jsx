import { connect } from 'react-redux'
import { compose } from 'redux'

import { withRequiredLogin } from '../../hocs'
import { assignData } from 'redux-saga-data'
import Offerers from './Offerers'
import { closeNotification, showNotification } from 'pass-culture-shared'
import { requestData } from 'redux-saga-data'
import { offererNormalizer } from '../../../utils/normalizers'

export const mapStateToProps = state => {
  return {
    pendingOfferers: state.data.pendingOfferers,
    offerers: state.data.offerers,
    notification: state.notification,
  }
}

export const mapDispatchToProps = (dispatch) => ({
  assignData:() => dispatch(assignData({ offerers: [], pendingOfferers: [] })),

  closeNotification:() => dispatch(closeNotification()),

  loadOfferers: (apiPath, handleFail, handleSuccess) => () => {
    dispatch(
      requestData({
        apiPath,
        handleFail: handleFail,
        handleSuccess: handleSuccess,
        normalizer: offererNormalizer,
      })
    )
  },

  loadNotValidatedUserOfferers: (notValidatedUserOfferersPath) => () => {
    dispatch(
      requestData({
        apiPath: notValidatedUserOfferersPath,
        normalizer: offererNormalizer,
        stateKey: 'pendingOfferers',
      })
    )
  },

  showNotification: (url) => () => {
    dispatch(
      showNotification({
        tag: 'offerers',
        text: 'Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)',
        type: 'info',
        url: url,
        urlLabel: 'Nouveau lieu'
      })
    )
  }
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Offerers)
