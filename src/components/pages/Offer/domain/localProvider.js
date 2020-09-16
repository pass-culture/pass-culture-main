const doesLastProviderExists = offer => offer !== null && offer.lastProvider

const isTiteLiveOffer = (offer = null) => {
  return doesLastProviderExists(offer)
    ? offer.lastProvider.name.toLowerCase().includes('titelive')
    : false
}

const isLibrairesOffer = (offer = null) => {
  return doesLastProviderExists(offer) ? offer.lastProvider.name === 'Leslibraires.fr' : false
}

const isAllocineOffer = (offer = null) => {
  return doesLastProviderExists(offer) ? offer.lastProvider.name === 'Allociné' : false
}

export { isAllocineOffer, isLibrairesOffer, isTiteLiveOffer }
