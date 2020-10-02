const doesLastProviderExists = offer => offer !== null && offer.lastProvider

export const localProvidersNames = [
  'fnac',
  'leslibraires.fr',
  'praxiel',
  'titelive (epagine / place des libraires.com)',
  'titelive stocks (epagine / place des libraires.com)',
]

const isOfferFromStockProvider = (offer = null) => {
  return doesLastProviderExists(offer)
    ? localProvidersNames.includes(offer.lastProvider.name.toLowerCase())
    : false
}

const isAllocineOffer = (offer = null) => {
  return doesLastProviderExists(offer)
    ? offer.lastProvider.name.toLowerCase() === 'allociné'
    : false
}

export { isAllocineOffer, isOfferFromStockProvider }
