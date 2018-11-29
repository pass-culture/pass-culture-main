import { withLogin } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'

import SearchPageContent from './SearchPageContent'
import { withQueryRouter } from '../hocs/withQueryRouter'
import { selectRecommendations } from '../../selectors'
import selectTypeSublabels, { selectTypes } from '../../selectors/selectTypes'

const mapStateToProps = state => {
  const recommendations = selectRecommendations(state)
  const typeSublabels = selectTypeSublabels(state)
  const typeSublabelsAndDescription = selectTypes(state)
  const user = { ...state }
  return {
    recommendations,
    typeSublabels,
    typeSublabelsAndDescription,
    user,
  }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  withQueryRouter,
  connect(mapStateToProps)
)(SearchPageContent)
