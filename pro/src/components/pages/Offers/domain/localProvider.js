import { CINEMA_PROVIDER_NAMES } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/VenueProvidersManager/utils/_constants'
import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'components/pages/Offers/Offer/OfferDetails/_constants'

const doesLastProviderExist = offer =>
  Boolean(offer !== null && offer.lastProvider)

export const isSynchronizedOffer = offer => {
  return isOfferFromStockProvider(offer) || isAllocineOffer(offer)
}

export const isOfferFromStockProvider = (offer = null) => {
  return doesLastProviderExist(offer)
}

export const isAllocineProvider = provider =>
  provider?.name.toLowerCase() === 'allociné'

export const isCinemaProvider = provider =>
  CINEMA_PROVIDER_NAMES.includes(provider?.name.toLowerCase())

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
