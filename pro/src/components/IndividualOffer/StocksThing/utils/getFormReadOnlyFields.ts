import type {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from '@/commons/core/Offers/constants'
import { isAllocineOffer } from '@/commons/core/Providers/utils/localProvider'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../constants'
import type { StockThingFormValues } from '../types'

export const getFormReadOnlyFields = (
  offer: GetIndividualOfferResponseModel,
  stocks: GetOfferStockResponseModel[],
  currentStock: StockThingFormValues
): string[] => {
  const isDisabledStatus = [
    OFFER_STATUS_REJECTED,
    OFFER_STATUS_PENDING,
  ].includes(offer.status)

  if (isDisabledStatus) {
    return Object.keys(STOCK_THING_FORM_DEFAULT_VALUES)
  }

  const isOfferSynchronized = Boolean(offer.lastProvider)
  const isOfferSynchronizedAllocine = isAllocineOffer(offer)

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
