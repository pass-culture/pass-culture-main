import {
  type GetIndividualOfferResponseModel,
  type GetOfferStockResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import { isAllocineProvider } from '@/commons/core/Providers/utils/utils'

import {
  type PriceTableFormValues,
  PriceTableValidationSchema,
} from '../schemas'

export const getFormReadOnlyFields = (
  offer: GetIndividualOfferResponseModel,
  stocks: GetOfferStockResponseModel[],
  currentStock: PriceTableFormValues
): string[] => {
  const isDisabledStatus = [OfferStatus.REJECTED, OfferStatus.PENDING].includes(
    offer.status
  )
  const isOfferSynchronized = !!offer.lastProvider
  const isOfferSynchronizedAllocine =
    offer.lastProvider && isAllocineProvider(offer.lastProvider)
  if (isDisabledStatus) {
    return Object.keys(PriceTableValidationSchema.fields)
  }

  if (isOfferSynchronized && !isOfferSynchronizedAllocine) {
    const readOnlyFields = Object.keys(PriceTableValidationSchema.fields)
    // we authorize the edition of stock quantity for synchronized offers
    // to avoid the creation of fake offers by pro users when
    // there is a discrepancy between their actual stock quantity
    // and the quantity sent by their provider
    return readOnlyFields.filter((field) => field !== 'quantity')
  }

  if (
    (currentStock.entries[0]?.activationCodes ?? []).length !== 0 ||
    (stocks.length > 0 && stocks[0].hasActivationCode)
  ) {
    return ['quantity']
  }
  return []
}
