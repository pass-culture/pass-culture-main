import { connect } from 'react-redux'
import { compose } from 'redux'

import { withRequiredLogin } from '../../hocs'
import Offerers from './Offerers'
import { closeNotification, showNotification } from 'pass-culture-shared'
import { assignData, requestData } from 'redux-saga-data'
import { offererNormalizer } from '../../../utils/normalizers'
import selectOfferers from '../../../selectors/selectOfferers'

import { OFFERERS_API_PATH } from '../../../config/apiPaths'

export const mapStateToProps = state => {
  return {
    offerers: selectOfferers(state),
    notification: state.notification,
  }
}

export const mapDispatchToProps = dispatch => ({
  closeNotification: () => dispatch(closeNotification()),

  loadOfferers: (handleSuccess, handleFail, loadOffererParameters = {}) => {
    let apiPath = OFFERERS_API_PATH
    let isValidated = loadOffererParameters.isValidated
    let keywords = loadOffererParameters.keywords

    if (isValidated !== undefined) {
      apiPath += `?validated=${isValidated}`
    }

    if (keywords !== undefined && keywords !== '') {
      apiPath += `&${keywords}`
    }

    dispatch(
      requestData({
        apiPath,
        handleFail,
        handleSuccess,
        normalizer: offererNormalizer,
      })
    )
  },

  showNotification: url => {
    dispatch(
      showNotification({
        tag: 'offerers',
        text:
          'Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)',
        type: 'info',
        url,
        urlLabel: 'Nouveau lieu',
      })
    )
  },

  resetLoadedOfferers: () => {
    dispatch(assignData({ offerers: [] }))
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Offerers)
