import { isOfferSynchronized } from 'core/Offers'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'
import { IOfferIndividual } from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'

import { FORM_DEFAULT_VALUES } from '../constants'

const setFormReadOnlyFields = (offer?: IOfferIndividual): string[] => {
  if (offer === undefined) {
    return []
  }

  if ([OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(offer.status)) {
    return Object.keys(FORM_DEFAULT_VALUES)
  }

  if (isOfferSynchronized(offer)) {
    let editableFields: string[] = []
    if (isAllocineProvider(offer.lastProvider)) {
      editableFields = ['isDuo']
    } else {
      editableFields = ['accessibility', 'externalTicketOfficeUrl']
    }
    return Object.keys(FORM_DEFAULT_VALUES).filter(
      (field: string) => !editableFields.includes(field)
    )
  } else {
    return [
      'categoryId',
      'subcategoryId',
      'offererId',
      'venueId',
      'showType',
      'showSubType',
      'musicType',
      'musicSubType',
    ]
  }
}

export default setFormReadOnlyFields
