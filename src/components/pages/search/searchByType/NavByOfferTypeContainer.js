import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData } from 'redux-saga-data'
import withQueryRouter from 'with-query-router'

import NavByOfferType from './NavByOfferType'

export const mapDispatchToProps = (dispatch, ownProps) => ({
  resetSearchStore: () => {
    dispatch(assignData({ searchRecommendations: [] }))
  },

  updateSearchQuery: typeSublabel => {
    const { query } = ownProps
    query.change(
      { categories: typeSublabel, page: null },
      { pathname: `/recherche/resultats/${typeSublabel}` }
    )
  },
})

export default compose(
  withQueryRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(NavByOfferType)
