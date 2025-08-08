import type { SelectOption } from '@/commons/custom_types/form'

import { type RecurrenceFormValues, RecurrenceType } from './types'

export const computeInitialValues = (
  priceCategoryOptions: SelectOption<number>[]
): RecurrenceFormValues => ({
  recurrenceType: RecurrenceType.UNIQUE,
  days: [],
  startingDate: '',
  endingDate: '',
  beginningTimes: [{ beginningTime: '' }],
  quantityPerPriceCategories: [
    {
      quantity: undefined,
      priceCategory:
        priceCategoryOptions.length === 1
          ? String(priceCategoryOptions[0].value)
          : '',
    },
  ],
  bookingLimitDateInterval: null,
  monthlyOption: null,
})
