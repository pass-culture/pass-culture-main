const doesLastProviderExists = offer => offer !== null && offer.lastProvider

const isTiteLiveOffer = (offer = null) => {
  return doesLastProviderExists(offer)
    ? offer.lastProvider.name.toLowerCase().includes('titelive')
    : false
}

const isLibrairesOffer = (offer = null) => {
  return doesLastProviderExists(offer)
    ? offer.lastProvider.name.toLowerCase() === 'leslibraires.fr'
    : false
}

const isAllocineOffer = (offer = null) => {
  return doesLastProviderExists(offer)
    ? offer.lastProvider.name.toLowerCase() === 'allociné'
    : false
}

const isFnacOffer = (offer = null) => {
  return doesLastProviderExists(offer) ? offer.lastProvider.name.toLowerCase() === 'fnac' : false
}

export { isAllocineOffer, isLibrairesOffer, isTiteLiveOffer, isFnacOffer }
