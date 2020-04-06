const isAllocineOffer = (offer = null) => {
  if (offer === null) {
    return false
  }

  const { lastProvider } = offer
  if (lastProvider === null) {
    return false
  }

  return lastProvider.name === 'Allociné'
}

export default isAllocineOffer
