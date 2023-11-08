import { GetOfferStockResponseModel } from 'apiClient/v1'
import {
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_PENDING,
} from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../constants'
import { StockThingFormValues } from '../types'

const setFormReadOnlyFields = (
  offer: IndividualOffer,
  stocks: GetOfferStockResponseModel[],
  currentStock: StockThingFormValues
): string[] => {
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

  if (
    currentStock.activationCodes?.length != 0 ||
    (stocks?.length > 0 && stocks[0].hasActivationCode)
  ) {
    return ['quantity']
  }
  return []
}
export default setFormReadOnlyFields
