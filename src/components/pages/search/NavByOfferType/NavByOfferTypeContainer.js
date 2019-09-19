import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData } from 'redux-thunk-data'

import NavByOfferType from './NavByOfferType'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'

export const mapDispatchToProps = (dispatch, ownProps) => ({
  resetSearchStore: () => {
    dispatch(assignData({ bookings: [], recommendations: [] }))
  },

  updateSearchQuery: categories => {
    const { query } = ownProps
    query.change({ categories, page: null }, { pathname: `/recherche/resultats/${categories}` })
  },
})

export default compose(
  withFrenchQueryRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(NavByOfferType)
