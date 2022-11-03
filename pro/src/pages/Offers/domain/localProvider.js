import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'core/Offers'
import { isAllocineProvider } from 'core/Providers'

const doesLastProviderExist = offer =>
  Boolean(offer !== null && offer.lastProvider)

export const isSynchronizedOffer = offer => {
  return isOfferFromStockProvider(offer) || isAllocineOffer(offer)
}

export const isOfferFromStockProvider = (offer = null) => {
  return doesLastProviderExist(offer)
}

export const isAllocineOffer = (offer = null) => {
  return doesLastProviderExist(offer)
    ? isAllocineProvider(offer.lastProvider)
    : false
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
