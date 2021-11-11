const isCancelView = match => {
  const { params } = match
  const { booking, confirmation } = params
  return typeof booking !== 'undefined' && typeof confirmation !== 'undefined'
}

export default isCancelView
