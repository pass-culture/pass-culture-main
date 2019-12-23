import { connect } from 'react-redux'

import MyBookingsLists from './MyBookingsLists'
import {
  selectEventBookingsOfTheWeek,
  selectCancelledBookings,
  selectFinishedEventBookings,
  selectUpComingBookings,
  selectUsedThingBookings,
} from '../../../../selectors/data/bookingsSelectors'
import { compose } from 'redux'
import { withRouter } from 'react-router-dom'

export const mapStateToProps = state => {
  const bookingsOfTheWeek = selectEventBookingsOfTheWeek(state)
  const cancelledBookings = selectCancelledBookings(state)
  const finishedEventBookings = selectFinishedEventBookings(state)
  const upComingBookings = selectUpComingBookings(state)
  const usedThingBookings = selectUsedThingBookings(state)
  const finishedAndUsedAndCancelledBookings = [
    ...finishedEventBookings,
    ...usedThingBookings,
    ...cancelledBookings,
  ]

  return { bookingsOfTheWeek, finishedAndUsedAndCancelledBookings, upComingBookings }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MyBookingsLists)
