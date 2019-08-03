import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData } from 'redux-saga-data'

import FilterControls from './FilterControls'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'

const mapDispatchToProps = dispatch => ({
  resetSearchStore: () => {
    dispatch(assignData({ bookings: [], recommendations: [] }))
  },
})

export default compose(
  withFrenchQueryRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(FilterControls)
