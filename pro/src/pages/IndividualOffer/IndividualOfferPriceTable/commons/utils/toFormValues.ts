import type { CastOptions } from 'yup'

import type {
  GetOfferStockResponseModel,
  PriceCategoryResponseModel,
} from '@/apiClient/v1'

import {
  PriceTableEntryValidationSchema,
  type PriceTableFormValues,
  PriceTableValidationSchema,
} from '../schemas'
import type { PriceTableFormContext } from '../types'

export function toFormValues(
  priceCategories: PriceCategoryResponseModel[],
  context: PriceTableFormContext
): PriceTableFormValues
export function toFormValues(
  offerStocks: GetOfferStockResponseModel[],
  context: PriceTableFormContext
): PriceTableFormValues
export function toFormValues(
  priceCategoriesOrOfferStocks:
    | PriceCategoryResponseModel[]
    | GetOfferStockResponseModel[],
  context: PriceTableFormContext
): PriceTableFormValues

export function toFormValues(
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
      entries:
        priceCategoriesOrOfferStocks.length > 0
          ? priceCategoriesOrOfferStocks.map((entry) => ({
              ...entry,
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
