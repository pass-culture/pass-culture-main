const isLibrairesOffer = (offer = null) => {
  if (offer === null) {
    return false
  }

  const { lastProvider } = offer
  if (lastProvider === null) {
    return false
  }

  return lastProvider.name === 'Leslibraires.fr'
}

export default isLibrairesOffer
