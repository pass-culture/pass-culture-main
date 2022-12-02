import { isBefore } from 'date-fns'

import { OfferStatus } from 'apiClient/v1'
import { OFFER_STATUS_PENDING, OFFER_STATUS_REJECTED } from 'core/Offers'
import { isAllocineProviderName } from 'core/Providers'
import { removeTime } from 'utils/date'

import {
  STOCK_EVENT_ALLOCINE_READ_ONLY_FIELDS,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
} from '../constants'

interface ISetReadOnlyFieldsArgs {
  beginningDate: Date | null
  today: Date
  lastProviderName: string | null
  offerStatus: OfferStatus
}

const setFormReadOnlyFields = ({
  beginningDate,
  today,
  lastProviderName,
  offerStatus,
}: ISetReadOnlyFieldsArgs) => {
  const isDisabledStatus = offerStatus
    ? [OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(offerStatus)
    : false

  const isOfferSynchronized = lastProviderName !== null
  const isOfferSynchronizedAllocine = isAllocineProviderName(lastProviderName)

  if (
    isDisabledStatus ||
    (beginningDate && isBefore(beginningDate, removeTime(today))) ||
    (isOfferSynchronized && !isOfferSynchronizedAllocine)
  ) {
    return Object.keys(STOCK_EVENT_FORM_DEFAULT_VALUES)
  } else if (isOfferSynchronizedAllocine) {
    return STOCK_EVENT_ALLOCINE_READ_ONLY_FIELDS
  }

  return []
}

export default setFormReadOnlyFields
