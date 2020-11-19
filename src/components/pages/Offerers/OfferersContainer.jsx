import { stringify } from 'query-string'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, requestData } from 'redux-saga-data'
import withQueryRouter from 'with-query-router'

import { OFFERERS_API_PATH } from 'config/apiPaths'
import {} from 'store/selectors/data/featuresSelectors'
import { closeNotification, showNotificationV1 } from 'store/reducers/notificationReducer'
import { isAPISireneAvailable } from 'store/selectors/data/featuresSelectors'
import { selectOfferers } from 'store/selectors/data/offerersSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { offererNormalizer } from 'utils/normalizers'

import Offerers from './Offerers'

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
    currentUser: selectCurrentUser(state),
    isOffererCreationAvailable: isAPISireneAvailable(state),
    notification: state.notification,
    offerers: selectOfferers(state),
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => ({
  closeNotification: () => dispatch(closeNotification()),

  loadOfferers: (handleSuccess, handleFail) => {
    const { query } = ownProps

    const queryParams = query.parse()
    let searchKeyWords = queryParams['mots-cles'] || []
    let pageParams = queryParams['page'] || '0'

    if (typeof searchKeyWords === 'string') searchKeyWords = [searchKeyWords]

    let apiPath = createApiPath(searchKeyWords)

    if (apiPath.includes('?')) {
      apiPath = `${apiPath}&page=${pageParams}`
    } else {
      apiPath = `${apiPath}?page=${pageParams}`
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

  resetLoadedOfferers: () => {
    dispatch(assignData({ offerers: [] }))
  },

  showNotification: url => {
    dispatch(
      showNotificationV1({
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

export default compose(withQueryRouter(), connect(mapStateToProps, mapDispatchToProps))(Offerers)
