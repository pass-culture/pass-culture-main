import { SelectOption } from 'custom_types/form'

import { RecurrenceFormValues, RecurrenceType } from './types'

export const computeInitialValues = (
  priceCategoryOptions: SelectOption[]
): RecurrenceFormValues => ({
  recurrenceType: RecurrenceType.UNIQUE,
  days: [],
  startingDate: null,
  endingDate: null,
  beginningTimes: [null],
  quantityPerPriceCategories: [
    {
      quantity: '',
      priceCategory:
        priceCategoryOptions.length === 1
          ? String(priceCategoryOptions[0].value)
          : '',
    },
  ],
  bookingLimitDateInterval: '',
  monthlyOption: null,
})
