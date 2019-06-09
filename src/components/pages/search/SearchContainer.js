import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import { Search } from './Search'
import { withRedirectToSigninOrTypeformAfterLogin } from '../../hocs'
import { selectRecommendations } from '../../../selectors'
import selectTypeSublabels, {
  selectTypes,
} from '../../../selectors/selectTypes'

const selectSearchRecommendations = state => {
  const recommendations = state.data.searchRecommendations || []
  const derivedState = { ...state, data: { ...state.data, recommendations } }

  return selectRecommendations(derivedState)
}

const mapStateToProps = state => {
  const recommendations = selectSearchRecommendations(state)
  const typeSublabels = selectTypeSublabels(state)
  const typeSublabelsAndDescription = selectTypes(state)
  const { user } = state

  return {
    recommendations,
    typeSublabels,
    typeSublabelsAndDescription,
    user,
  }
}

export const SearchContainer = compose(
  withRedirectToSigninOrTypeformAfterLogin,
  withQueryRouter,
  connect(mapStateToProps)
)(Search)
