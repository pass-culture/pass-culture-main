import { connect } from 'react-redux'
import { compose } from 'redux'

import { withLogin, withPagination } from 'pass-culture-shared'
import { translateBrowserUrlToApiUrl } from './search/utils'

import SearchPageContent from './SearchPageContent'
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
  withPagination({
    dataKey: 'recommendations',
    defaultWindowQuery: {
      categories: null,
      date: null,
      distance: null,
      jours: null,
      latitude: null,
      longitude: null,
      'mots-cles': null,
      orderBy: 'offer.id+desc',
    },
    windowToApiQuery: translateBrowserUrlToApiUrl,
  }),
  connect(mapStateToProps)
)(SearchPageContent)
