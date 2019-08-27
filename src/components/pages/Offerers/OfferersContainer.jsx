import { connect } from 'react-redux'
import { compose } from 'redux'

import { withRequiredLogin } from '../../hocs'
import { requestData } from 'redux-saga-data'
import Offerers from './Offerers'
import { closeNotification, showNotification } from 'pass-culture-shared'
import { assignData } from 'fetch-normalize-data'
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
  assignData: () => dispatch(assignData({ offerers: [] })),

  closeNotification: () => dispatch(closeNotification()),

  loadOfferers: (handleFail, handleSuccess, { isValidated } = {}) => {
    let apiPath = OFFERERS_API_PATH

    if (isValidated !== undefined) apiPath += `?validated=${isValidated}`

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
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Offerers)
