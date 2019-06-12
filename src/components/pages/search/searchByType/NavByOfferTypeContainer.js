import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData } from 'redux-saga-data'
import withQueryRouter from 'with-query-router'

import NavByOfferType from './NavByOfferType'

export const mapDispatchToProps = (dispatch, ownProps) => ({
  resetSearchStore: () => {
    dispatch(assignData({ searchRecommendations: [] }))
  },

  updateSearchQuery: categories => {
    const { query } = ownProps
    query.change(
      { categories, page: null },
      { pathname: `/recherche/resultats/${categories}` }
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
