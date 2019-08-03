const getIsCancelling = match => {
  const { params } = match
  const { bookings, cancellation, confirmation } = params
  return (
    typeof bookings !== 'undefined' &&
    typeof cancellation !== 'undefined' &&
    typeof confirmation === 'undefined'
  )
}

export default getIsCancelling
