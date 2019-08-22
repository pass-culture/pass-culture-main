import { connect } from 'react-redux'

import MyBookingsLists from './MyBookingsLists'
import selectOtherBookings from './selectors/selectOtherBookings'
import selectSoonBookings from './selectors/selectSoonBookings'
import { compose } from 'redux'
import { withRouter } from 'react-router-dom'

export const mapStateToProps = state => {
  const otherBookings = selectOtherBookings(state)
  const soonBookings = selectSoonBookings(state)
  return { otherBookings, soonBookings }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MyBookingsLists)
