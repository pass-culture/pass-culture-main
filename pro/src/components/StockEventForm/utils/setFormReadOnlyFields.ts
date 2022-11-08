import { isBefore } from 'date-fns'

import { OFFER_STATUS_PENDING, OFFER_STATUS_REJECTED } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'
import { removeTime } from 'utils/date'

import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../constants'

const setFormReadOnlyFields = (
  offer: IOfferIndividual,
  beginningDate: Date | null,
  today: Date
) => {
  const isDisabledStatus = offer.status
    ? [OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(offer.status)
    : false
  const isOfferSynchronized = !!offer.lastProvider
  const isOfferSynchronizedAllocine =
    offer.lastProvider && isAllocineProvider(offer.lastProvider)
  if (
    isDisabledStatus ||
    (beginningDate && isBefore(beginningDate, removeTime(today))) ||
    (isOfferSynchronized && !isOfferSynchronizedAllocine)
  ) {
    return Object.keys(STOCK_EVENT_FORM_DEFAULT_VALUES)
  }
  return []
}

export default setFormReadOnlyFields
