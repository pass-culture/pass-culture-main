import { isOfferSynchronized } from 'core/Offers'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'
import { IOfferIndividual } from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'

import { FORM_DEFAULT_VALUES } from '../constants'

const setFormReadOnlyFields = (
  offer: IOfferIndividual | null,
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
      editableFields = ['isDuo']
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
      ...[
        'categoryId',
        'subcategoryId',
        'offererId',
        'venueId',
        'showType',
        'showSubType',
        'musicType',
        'musicSubType',
      ],
    ]
  }

  return [...new Set(readOnlyField)]
}

export default setFormReadOnlyFields
