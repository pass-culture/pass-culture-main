import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'core/Offers'
import {
  IOfferIndividual,
  IOfferIndividualVenueProvider,
} from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'

// can be deleted with FF OFFER_FORM_V3
export const isSynchronizedOffer = (
  offer: IOfferIndividual | null | undefined = null
) => {
  return !!offer?.lastProvider || isAllocineOffer(offer)
}

export const isAllocineOffer = (
  offer: IOfferIndividual | null | undefined = null
) => {
  return offer?.lastProvider ? isAllocineProvider(offer?.lastProvider) : false
}

// can be deleted with FF OFFER_FORM_V3
export const isFieldReadOnlyForSynchronizedOffer = (
  fieldName: string,
  provider: IOfferIndividualVenueProvider | null
): boolean => {
  const {
    ALLOCINE: allocineEditableFields,
    ALL_PROVIDERS: allProvidersEditableFields,
  } = SYNCHRONIZED_OFFER_EDITABLE_FIELDS
  const editableFields = isAllocineProvider(provider)
    ? [...allocineEditableFields, ...allProvidersEditableFields]
    : allProvidersEditableFields

  return !editableFields.includes(fieldName)
}
