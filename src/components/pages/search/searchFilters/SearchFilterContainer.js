import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData } from 'redux-saga-data'
import withQueryRouter from 'with-query-router'

import { SearchFilter } from './SearchFilter'

const mapDispatchToProps = dispatch => ({
  resetSearchStore: () => {
    dispatch(assignData({ searchRecommendations: [] }))
  },
})

export const SearchFilterContainer = compose(
  withQueryRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(SearchFilter)
