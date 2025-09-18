import type {
  CreatePriceCategoryModel,
  PriceCategoryBody,
} from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

import type { PriceTableFormValues } from '../schemas'

export const toPriceCategoryBody = (
  formValues: PriceTableFormValues
): PriceCategoryBody => {
  return {
    priceCategories: formValues.entries.map((entry) => {
      assertOrFrontendError(entry.label, '`entry.label` is undefined.')

      return {
        ...(entry.id === undefined ? {} : { id: entry.id }),
        label: entry.label,
        price: entry.price ?? 0,
      } satisfies CreatePriceCategoryModel
    }),
  }
}
