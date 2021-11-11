const getIsBooking = match => {
  const { params } = match
  const { booking, cancellation, confirmation } = params

  if (typeof cancellation !== 'undefined') {
    return typeof confirmation !== 'undefined'
  }

  return typeof booking !== 'undefined'
}

export default getIsBooking
