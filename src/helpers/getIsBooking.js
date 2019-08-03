const getIsBooking = match => {
  const { params } = match
  const { bookings, cancellation, confirmation } = params

  if (typeof cancellation !== 'undefined') {
    return typeof confirmation !== 'undefined'
  }

  return typeof bookings !== 'undefined'
}

export default getIsBooking
