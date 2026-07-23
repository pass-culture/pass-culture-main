import type {
  PriceCategoryBody,
  UpsertPriceCategoryModel,
} from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

import type { PriceTableFormValues } from '../schemas'

export const toPriceCategoryBody = (
  formValues: PriceTableFormValues
): PriceCategoryBody => {
  return {
    priceCategories: formValues.priceCategories.map((entry) => {
      assertOrFrontendError(entry.label, '`entry.label` is undefined.')

      return {
        id: entry.id,
        label: entry.label,
        price: entry.price ?? 0,
      } satisfies UpsertPriceCategoryModel
    }),
  }
}
