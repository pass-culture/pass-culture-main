import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData } from 'redux-saga-data'

import SearchFilter from './SearchFilter'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'

const mapDispatchToProps = dispatch => ({
  resetSearchStore: () => {
    dispatch(assignData({ searchRecommendations: [] }))
  },
})

export default compose(
  withFrenchQueryRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(SearchFilter)
