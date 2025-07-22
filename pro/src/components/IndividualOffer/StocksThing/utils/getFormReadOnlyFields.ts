import {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import {
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_PENDING,
} from 'commons/core/Offers/constants'
import { isAllocineProvider } from 'commons/core/Providers/utils/utils'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../constants'
import { StockThingFormValues } from '../types'

export const getFormReadOnlyFields = (
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
  if (isDisabledStatus) {
    return Object.keys(STOCK_THING_FORM_DEFAULT_VALUES)
  }

  if (isOfferSynchronized && !isOfferSynchronizedAllocine) {
    const readOnlyFields = Object.keys(STOCK_THING_FORM_DEFAULT_VALUES)
    // we authorize the edition of stock quantity for synchronized offers
    // to avoid the creation of fake offers by pro users when
    // there is a discrepancy between their actual stock quantity
    // and the quantity sent by their provider
    return readOnlyFields.filter((field) => field !== 'quantity')
  }

  if (
    (currentStock.activationCodes ?? []).length !== 0 ||
    (stocks.length > 0 && stocks[0].hasActivationCode)
  ) {
    return ['quantity']
  }
  return []
}
