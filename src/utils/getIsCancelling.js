const getIsCancelling = match => {
  const { params } = match
  const { booking, cancellation, confirmation } = params
  return (
    typeof booking !== 'undefined' &&
    typeof cancellation !== 'undefined' &&
    typeof confirmation === 'undefined'
  )
}

export default getIsCancelling
