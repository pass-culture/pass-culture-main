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
  let apiQueryParams = {}

  if (searchKeyWords.length > 0) {
    apiPath += '?'
    apiQueryParams.keywords = searchKeyWords.join(' ')
  }

  const queryParams = stringify(apiQueryParams)

  return apiPath + queryParams
}

export const mapStateToProps = state => {
  return {
    offerers: selectOfferers(state),
    notification: state.notification,
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => ({
  closeNotification: () => dispatch(closeNotification()),

  loadOfferers: (handleSuccess, handleFail) => {
    const { query } = ownProps

    const queryParams = query.parse()
    let searchKeyWords = queryParams['mots-cles'] || []

    if (typeof searchKeyWords === 'string') searchKeyWords = [searchKeyWords]

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
