import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'core/Offers'
import {
  IOfferIndividual,
  IOfferIndividualVenueProvider,
} from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'

const doesLastProviderExist = (
  offer: IOfferIndividual | null | undefined = null
) => Boolean(offer !== null && offer.lastProvider)

export const isSynchronizedOffer = (
  offer: IOfferIndividual | null | undefined = null
) => {
  return isOfferFromStockProvider(offer) || isAllocineOffer(offer)
}

export const isOfferFromStockProvider = (
  offer: IOfferIndividual | null | undefined = null
) => {
  return doesLastProviderExist(offer)
}

export const isAllocineOffer = (
  offer: IOfferIndividual | null | undefined = null
) => {
  return doesLastProviderExist(offer)
    ? isAllocineProvider(offer?.lastProvider)
    : false
}

export const isFieldReadOnlyForSynchronizedOffer = (
  fieldName: string,
  provider: IOfferIndividualVenueProvider | null
): boolean => {
  const {
    ALLOCINE: allocineEditableFields,
    OTHER_PROVIDERS: allProvidersEditableFields,
  } = SYNCHRONIZED_OFFER_EDITABLE_FIELDS
  const editableFields = isAllocineProvider(provider)
    ? [...allocineEditableFields, ...allProvidersEditableFields]
    : allProvidersEditableFields

  return !editableFields.includes(fieldName)
}
