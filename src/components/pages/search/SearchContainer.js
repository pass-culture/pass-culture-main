import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import Search from './Search'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import {
  selectTypes,
  selectTypeSublabels,
  selectTypeSublabelsAndDescription,
} from '../../../selectors/data/typesSelectors'
import { selectRecommendationsBySearchQuery } from '../../../selectors/data/recommendationsSelectors'
import { recommendationNormalizer } from '../../../utils/normalizers'
import { updatePage } from '../../../reducers/pagination'

export const mapStateToProps = (state, ownProps) => {
  const recommendations = selectRecommendationsBySearchQuery(state, ownProps.location)
  const typeSublabels = selectTypeSublabels(state)
  const typeSublabelsAndDescription = selectTypeSublabelsAndDescription(state)
  const types = selectTypes(state)
  const { user } = state

  return {
    recommendations,
    typeSublabels,
    typeSublabelsAndDescription,
    user,
    types,
  }
}

export const mapDispatchToProps = dispatch => ({
  getRecommendations: (apiPath, handleSuccess) => {
    apiPath = decodeURIComponent(apiPath)
    dispatch(
      requestData({
        apiPath,
        handleSuccess,
        normalizer: recommendationNormalizer,
      })
    )
    dispatch(
      updatePage(1)
    )
  },

  getTypes: () => {
    dispatch(requestData({ apiPath: '/types' }))
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Search)
