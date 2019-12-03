import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, requestData } from 'redux-thunk-data'

import Search from './Search'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import {
  selectTypeSublabels,
  selectTypeSublabelsAndDescription,
} from '../../../selectors/data/typesSelectors'
import { selectSearchedRecommendations } from '../../../selectors/data/searchedRecommendationsSelectors'
import { recommendationNormalizer } from '../../../utils/normalizers'
import { updatePage } from '../../../reducers/pagination'

export const mapStateToProps = state => {
  const searchedRecommendations = selectSearchedRecommendations(state)
  const typeSublabels = selectTypeSublabels(state)
  const typeSublabelsAndDescription = selectTypeSublabelsAndDescription(state)
  const { user } = state

  return {
    searchedRecommendations,
    typeSublabels,
    typeSublabelsAndDescription,
    user,
  }
}

export const mapDispatchToProps = dispatch => ({
  getSearchedRecommendations: (apiPath, handleSuccess) => {
    apiPath = decodeURIComponent(apiPath)
    dispatch(
      requestData({
        apiPath,
        handleSuccess,
        normalizer: recommendationNormalizer,
        stateKey: 'searchedRecommendations',
      })
    )
    dispatch(updatePage(1))
  },

  getTypes: () => {
    dispatch(requestData({ apiPath: '/types' }))
  },

  resetSearchedRecommendations: () => {
    dispatch(assignData({ searchedRecommendations: [] }))
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Search)
