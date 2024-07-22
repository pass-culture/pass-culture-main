import { SelectOption } from 'custom_types/form'

import { RecurrenceFormValues, RecurrenceType } from './types'

export const computeInitialValues = (
  priceCategoryOptions: SelectOption[]
): RecurrenceFormValues => ({
  recurrenceType: RecurrenceType.UNIQUE,
  days: [],
  startingDate: '',
  endingDate: '',
  beginningTimes: [''],
  quantityPerPriceCategories: [
    {
      quantity: '',
      priceCategory: priceCategoryOptions[0]
        ? String(priceCategoryOptions[0].value)
        : '',
    },
  ],
  bookingLimitDateInterval: '',
  monthlyOption: null,
})
