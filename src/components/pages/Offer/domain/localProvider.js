import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'components/pages/Offer/Offer/OfferDetails/OfferForm/_constants'

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

const isAllocineProvider = provider => provider?.name.toLowerCase() === 'allociné'

export const isAllocineOffer = (offer = null) => {
  return doesLastProviderExist(offer) ? isAllocineProvider(offer.lastProvider) : false
}

export const isFieldReadOnlyForSynchronizedOffer = (fieldName, provider) => {
  const {
    ALLOCINE: allocineEditableFields,
    ALL_PROVIDERS: allProvidersEditableFields,
  } = SYNCHRONIZED_OFFER_EDITABLE_FIELDS
  const editableFields = isAllocineProvider(provider)
    ? [...allocineEditableFields, ...allProvidersEditableFields]
    : allProvidersEditableFields

  return !editableFields.includes(fieldName)
}
