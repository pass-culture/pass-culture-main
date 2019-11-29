import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, requestData } from 'redux-thunk-data'

import Search from './Search'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import {
  selectTypeSublabels,
  selectTypeSublabelsAndDescription,
} from '../../../selectors/data/typesSelectors'
import { selectResearchedRecommendations } from '../../../selectors/data/researchedRecommendationsSelectors'
import { recommendationNormalizer } from '../../../utils/normalizers'
import { updatePage } from '../../../reducers/pagination'

export const mapStateToProps = state => {
  const researchedRecommendations = selectResearchedRecommendations(state)
  const typeSublabels = selectTypeSublabels(state)
  const typeSublabelsAndDescription = selectTypeSublabelsAndDescription(state)
  const { user } = state

  return {
    researchedRecommendations,
    typeSublabels,
    typeSublabelsAndDescription,
    user,
  }
}

export const mapDispatchToProps = dispatch => ({
  getResearchedRecommendations: (apiPath, handleSuccess) => {
    apiPath = decodeURIComponent(apiPath)
    dispatch(
      requestData({
        apiPath,
        handleSuccess,
        normalizer: recommendationNormalizer,
        stateKey: 'researchedRecommendations',
      })
    )
    dispatch(updatePage(1))
  },

  getTypes: () => {
    dispatch(requestData({ apiPath: '/types' }))
  },

  resetSearchStore: () => {
    dispatch(assignData({ researchedRecommendations: [] }))
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Search)
