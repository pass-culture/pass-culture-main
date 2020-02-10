import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, requestData } from 'redux-saga-data'
import { closeNotification, showNotification } from 'pass-culture-shared'
import { stringify } from 'query-string'

import Offerers from './Offerers'
import { withRequiredLogin } from '../../hocs'
import { offererNormalizer } from '../../../utils/normalizers'
import { selectOfferers } from '../../../selectors/data/offerersSelectors'

import { OFFERERS_API_PATH } from '../../../config/apiPaths'

export const createApiPath = searchKeyWords => {
  let apiPath = OFFERERS_API_PATH
  if (Array.isArray(searchKeyWords)) {
    searchKeyWords = searchKeyWords.join(' ')
  }
  const isKeywordValidParam =
    searchKeyWords !== undefined && searchKeyWords !== null && searchKeyWords !== ''

  if (isKeywordValidParam) {
    const urlSearchKeyWords = stringify({ keywords: searchKeyWords })
    apiPath += `?${urlSearchKeyWords}`
  }

  return apiPath
}

export const mapStateToProps = state => {
  return {
    offerers: selectOfferers(state),
    notification: state.notification,
  }
}

export const mapDispatchToProps = dispatch => ({
  closeNotification: () => dispatch(closeNotification()),

  loadOfferers: (handleSuccess, handleFail, searchKeyWords) => {
    const apiPath = createApiPath(searchKeyWords)

    dispatch(
      requestData({
        apiPath,
        handleFail,
        handleSuccess,
        normalizer: offererNormalizer,
      })
    )
  },

  resetLoadedOfferers: () => {
    dispatch(assignData({ offerers: [] }))
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
