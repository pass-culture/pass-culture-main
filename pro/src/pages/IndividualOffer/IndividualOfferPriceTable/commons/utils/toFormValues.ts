import { format } from 'date-fns'
import type { CastOptions } from 'yup'

import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  PriceCategoryResponseModel,
} from '@/apiClient/v1'
import { FORMAT_ISO_DATE_ONLY, isDateValid } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

import {
  PriceTableEntryValidationSchema,
  type PriceTableFormValues,
  PriceTableValidationSchema,
} from '../schemas'
import type { PriceTableFormContext } from '../types'

const isGetOfferStockResponseModel = (
  entry: PriceCategoryResponseModel | GetOfferStockResponseModel
): entry is GetOfferStockResponseModel => {
  return 'quantity' in entry
}

export function toFormValues(
  offer: GetIndividualOfferWithAddressResponseModel,
  priceCategories: PriceCategoryResponseModel[],
  context: PriceTableFormContext
): PriceTableFormValues
export function toFormValues(
  offer: GetIndividualOfferWithAddressResponseModel,
  offerStocks: GetOfferStockResponseModel[],
  context: PriceTableFormContext
): PriceTableFormValues
export function toFormValues(
  offer: GetIndividualOfferWithAddressResponseModel,
  priceCategoriesOrOfferStocks:
    | PriceCategoryResponseModel[]
    | GetOfferStockResponseModel[],
  context: PriceTableFormContext
): PriceTableFormValues

export function toFormValues(
  offer: GetIndividualOfferWithAddressResponseModel,
  priceCategoriesOrOfferStocks:
    | PriceCategoryResponseModel[]
    | GetOfferStockResponseModel[],
  context: PriceTableFormContext
): PriceTableFormValues {
  const castOptions: CastOptions = {
    assert: false,
    stripUnknown: true,
    context,
  }

  return PriceTableValidationSchema.cast(
    {
      ...offer,
      entries:
        priceCategoriesOrOfferStocks.length > 0
          ? priceCategoriesOrOfferStocks.map((entry) => ({
              ...entry,
              activationCodesExpirationDatetime:
                isGetOfferStockResponseModel(entry) &&
                entry.activationCodesExpirationDatetime &&
                isDateValid(entry.activationCodesExpirationDatetime)
                  ? format(
                      new Date(entry.activationCodesExpirationDatetime),
                      FORMAT_ISO_DATE_ONLY
                    )
                  : null,
              bookingLimitDatetime:
                isGetOfferStockResponseModel(entry) &&
                entry.bookingLimitDatetime
                  ? format(
                      getLocalDepartementDateTimeFromUtc(
                        entry.bookingLimitDatetime,
                        getDepartmentCode(offer)
                      ),
                      FORMAT_ISO_DATE_ONLY
                    )
                  : null,
              offerId: context.offer.id,
            }))
          : [
              PriceTableEntryValidationSchema.cast(
                {
                  label: context.offer.isEvent ? 'Tarif unique' : null,
                  offerId: context.offer.id,
                },
                castOptions
              ),
            ],
    },
    castOptions
  )
}
