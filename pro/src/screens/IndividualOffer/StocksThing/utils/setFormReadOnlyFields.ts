import {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import {
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_PENDING,
} from 'core/Offers/constants'
import { isAllocineProvider } from 'core/Providers/utils/utils'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../constants'
import { StockThingFormValues } from '../types'

export const setFormReadOnlyFields = (
  offer: GetIndividualOfferResponseModel,
  stocks: GetOfferStockResponseModel[],
  currentStock: StockThingFormValues
): string[] => {
  const isDisabledStatus = [
    OFFER_STATUS_REJECTED,
    OFFER_STATUS_PENDING,
  ].includes(offer.status)
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
    currentStock.activationCodes.length !== 0 ||
    (stocks.length > 0 && stocks[0].hasActivationCode)
  ) {
    return ['quantity']
  }
  return []
}
