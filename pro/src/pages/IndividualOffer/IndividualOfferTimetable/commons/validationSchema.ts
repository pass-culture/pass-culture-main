import type { ObjectSchema } from 'yup'
import * as yup from 'yup'

import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'

import type { QuantityPerPriceCategoryForm } from '../components/StocksCalendar/form/types'
import { HasDateEnum, type IndividualOfferTimetableFormValues } from './types'

export const validationSchema: ObjectSchema<IndividualOfferTimetableFormValues> =
  yup.object().shape({
    startDate: nonEmptyStringOrNull(),
    hasEndDate: yup
      .mixed<HasDateEnum>()
      .oneOf(Object.values(HasDateEnum))
      .required(),
    hasStartDate: yup
      .mixed<HasDateEnum>()
      .oneOf(Object.values(HasDateEnum))
      .required(),
    endDate: nonEmptyStringOrNull(),
    quantityPerPriceCategories: yup.array<QuantityPerPriceCategoryForm>(),
  })
