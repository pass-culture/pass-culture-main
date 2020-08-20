import { connect } from 'react-redux'
import { FEATURES } from '../../../router/selectors/features'
import selectIsFeatureDisabled from '../../../router/selectors/selectIsFeatureDisabled'

import MyBookingsLists from './MyBookingsLists'
import {
  selectEventBookingsOfTheWeek,
  selectCancelledBookings,
  selectFinishedEventBookings,
  selectUpComingBookings,
  selectUsedThingBookings,
} from '../../../../redux/selectors/data/bookingsSelectors'
import { compose } from 'redux'
import { withRouter } from 'react-router-dom'

export const mapStateToProps = state => {
  const bookingsOfTheWeek = selectEventBookingsOfTheWeek(state)
  const cancelledBookings = selectCancelledBookings(state)
  const finishedEventBookings = selectFinishedEventBookings(state)
  const isHomepageDisabled = selectIsFeatureDisabled(state, FEATURES.HOMEPAGE)
  const upComingBookings = selectUpComingBookings(state)
  const usedThingBookings = selectUsedThingBookings(state)
  const finishedAndUsedAndCancelledBookings = [
    ...finishedEventBookings,
    ...usedThingBookings,
    ...cancelledBookings,
  ]

  return {
    bookingsOfTheWeek,
    finishedAndUsedAndCancelledBookings,
    isHomepageDisabled,
    upComingBookings,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MyBookingsLists)
