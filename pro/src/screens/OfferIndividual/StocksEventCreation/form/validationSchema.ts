import * as yup from 'yup'

import { oneOfSelectOption } from 'core/shared/utils/validation'
import { SelectOption } from 'custom_types/form'

import { RecurrenceType } from './types'

export const getValidationSchema = (priceCategoriesOptions: SelectOption[]) =>
  yup.object().shape({
    recurrenceType: yup
      .string()
      .required()
      .oneOf(Object.values(RecurrenceType)),
    startingDate: yup
      .date()
      .nullable()
      .transform((curr, orig) => (orig === null ? null : curr))
      .when('recurrenceType', {
        is: RecurrenceType.UNIQUE,
        then: schema => schema.required('Veuillez renseigner une date'),
        otherwise: schema =>
          schema.required('Veuillez renseigner une date de début'),
      }),
    endingDate: yup
      .date()
      .nullable('Veuillez renseigner une date de fin')
      .transform((curr, orig) => (orig === null ? null : curr))
      .when('recurrenceType', {
        is: RecurrenceType.DAILY,
        then: schema => schema.required('Veuillez renseigner une date de fin'),
      }),
    beginningTimes: yup
      .array()
      .of(yup.string().nullable().required('Veuillez renseigner un horaire')),
    quantityPerPriceCategories: yup.array().of(
      yup.object().shape({
        quantity: yup.number(),
        priceCategory: oneOfSelectOption(
          yup.string().required('Veuillez renseigner un tarif'),
          priceCategoriesOptions
        ),
      })
    ),
    bookingLimitDateInterval: yup.number(),
  })
