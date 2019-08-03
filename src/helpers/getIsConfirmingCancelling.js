const getIsConfirmingCancelling = match => {
  const { params } = match
  const { bookings, confirmation } = params
  return typeof bookings !== 'undefined' && typeof confirmation !== 'undefined'
}

export default getIsConfirmingCancelling
