import { connect } from 'react-redux'

import MyBookingsLists from './MyBookingsLists'
import {
  selectBookingsOfTheWeek,
  selectCancelledBookings,
  selectFinishedBookings,
  selectUpComingBookings,
  selectUsedBookings,
} from '../../../../selectors/data/bookingsSelectors'
import { compose } from 'redux'
import { withRouter } from 'react-router-dom'

export const mapStateToProps = state => {
  const bookingsOfTheWeek = selectBookingsOfTheWeek(state)
  const cancelledBookings = selectCancelledBookings(state)
  const finishedBookings = selectFinishedBookings(state)
  const upComingBookings = selectUpComingBookings(state)
  const usedBookings = selectUsedBookings(state)
  const finishedAndUsedAndCancelledBookings = [
    ...finishedBookings,
    ...usedBookings,
    ...cancelledBookings,
  ]

  return { bookingsOfTheWeek, finishedAndUsedAndCancelledBookings, upComingBookings }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MyBookingsLists)
