import {
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_PENDING,
} from 'core/Offers/constants'
import { IOfferIndividual } from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../constants'

const setFormReadOnlyFields = (offer: IOfferIndividual): string[] => {
  const isDisabledStatus = offer.status
    ? [OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(offer.status)
    : false
  const isOfferSynchronized = !!offer.lastProvider
  const isOfferSynchronizedAllocine =
    offer.lastProvider && isAllocineProvider(offer.lastProvider)
  if (
    isDisabledStatus ||
    (isOfferSynchronized && !isOfferSynchronizedAllocine)
  ) {
    return Object.keys(STOCK_THING_FORM_DEFAULT_VALUES)
  }
  return []
}
export default setFormReadOnlyFields
