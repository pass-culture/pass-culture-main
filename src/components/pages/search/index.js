import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import RawSearch from './RawSearch'
import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs'
import { selectRecommendations } from '../../../selectors'
import selectTypeSublabels, {
  selectTypes,
} from '../../../selectors/selectTypes'

const mapStateToProps = state => {
  const recommendations = selectRecommendations(state)
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

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withQueryRouter,
  connect(mapStateToProps)
)(RawSearch)
