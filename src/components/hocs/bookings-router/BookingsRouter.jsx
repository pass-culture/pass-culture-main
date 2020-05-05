import PropTypes from 'prop-types'
import React from 'react'

import BookingsContainer from '../../pages/Bookings/BookingsContainer'
import BookingsContainerV2 from '../../pages/Bookings-v2/BookingsRecapContainer'

const BookingsRouter = ({ isBookingsV2Active }) =>
  isBookingsV2Active ? <BookingsContainerV2 /> : <BookingsContainer />

BookingsRouter.defaultProps = {
  isBookingsV2Active: false,
}

BookingsRouter.propTypes = {
  isBookingsV2Active: PropTypes.bool,
}

export default BookingsRouter
