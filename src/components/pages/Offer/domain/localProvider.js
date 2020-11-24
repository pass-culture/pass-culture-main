const doesLastProviderExist = offer => offer !== null && offer.lastProvider

export const localProvidersNames = [
  'fnac',
  'leslibraires.fr',
  'praxiel/inférence',
  'titelive (epagine / place des libraires.com)',
  'titelive stocks (epagine / place des libraires.com)',
]

export const isSynchronizedOffer = (offer = null) => {
  return isOfferFromStockProvider(offer) || isAllocineOffer(offer)
}

export const isOfferFromStockProvider = (offer = null) => {
  return doesLastProviderExist(offer)
    ? localProvidersNames.includes(offer.lastProvider.name.toLowerCase())
    : false
}

export const isAllocineOffer = (offer = null) => {
  return doesLastProviderExist(offer) ? offer.lastProvider.name.toLowerCase() === 'allociné' : false
}
