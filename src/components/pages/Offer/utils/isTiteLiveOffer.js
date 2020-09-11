const isTiteLiveOffer = (offer = null) => {
  if (offer === null) {
    return false
  }

  const { lastProvider } = offer
  if (!lastProvider) {
    return false
  }

  return lastProvider.name.toLowerCase().includes('titelive')
}

export default isTiteLiveOffer
