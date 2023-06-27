import { isOfferSynchronized } from 'core/Offers'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'
import { OfferIndividual } from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'

import { FORM_DEFAULT_VALUES } from '../constants'

const setFormReadOnlyFields = (
  offer: OfferIndividual | null,
  isAdmin?: boolean
): string[] => {
  let readOnlyField: string[] = []

  if (isAdmin === true) {
    readOnlyField.push('offererId')
  }

  if (offer === null) {
    return readOnlyField
  }

  if ([OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(offer.status)) {
    readOnlyField = [...readOnlyField, ...Object.keys(FORM_DEFAULT_VALUES)]
  }

  if (isOfferSynchronized(offer)) {
    let editableFields: string[] = []
    if (isAllocineProvider(offer.lastProvider)) {
      editableFields = ['isDuo', 'accessibility', 'externalTicketOfficeUrl']
    } else {
      editableFields = ['accessibility', 'externalTicketOfficeUrl']
    }
    readOnlyField = [
      ...readOnlyField,
      ...Object.keys(FORM_DEFAULT_VALUES).filter(
        (field: string) => !editableFields.includes(field)
      ),
    ]
  } else {
    readOnlyField = [
      ...readOnlyField,
      ...['categoryId', 'subcategoryId', 'offererId', 'venueId'],
    ]
  }

  return [...new Set(readOnlyField)]
}

export default setFormReadOnlyFields
