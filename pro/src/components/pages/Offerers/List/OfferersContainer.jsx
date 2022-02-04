import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, requestData } from 'redux-saga-data'

import { withQueryRouter } from 'components/hocs/with-query-router/withQueryRouter'
import { OFFERERS_API_PATH } from 'config/apiPaths'
import { isAPISireneAvailable } from 'store/features/selectors'
import { selectOfferers } from 'store/selectors/data/offerersSelectors'
import { offererNormalizer } from 'utils/normalizers'
import { stringify } from 'utils/query-string'

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
    isOffererCreationAvailable: isAPISireneAvailable(state),
    offerers: selectOfferers(state),
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => ({
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
})

export default compose(
  withQueryRouter(),
  connect(mapStateToProps, mapDispatchToProps)
)(Offerers)
