import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'components/pages/Offers/Offer/OfferDetails/_constants'

const doesLastProviderExist = offer => Boolean(offer !== null && offer.lastProvider)

export const isSynchronizedOffer = (offer = null) => {
  return isOfferFromStockProvider(offer) || isAllocineOffer(offer)
}

export const isOfferFromStockProvider = (offer = null) => {
  return doesLastProviderExist(offer)
}

export const isAllocineProvider = provider => provider?.name.toLowerCase() === 'allociné'

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
