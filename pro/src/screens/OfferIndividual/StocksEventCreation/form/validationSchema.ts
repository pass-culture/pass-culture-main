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
    quantityPerPriceCategories: yup
      .array()
      .of(
        yup.object().shape({
          quantity: yup.number(),
          priceCategory: oneOfSelectOption(
            yup.string().required('Veuillez renseigner un tarif'),
            priceCategoriesOptions
          ),
        })
      )
      .test('isPriceCategoryUnique', function (list) {
        if (!list) return
        const price_category_map = list.map(a => a.priceCategory)
        const duplicateIndex = price_category_map.reduce<yup.ValidationError[]>(
          (ac, a, i) => {
            if (
              price_category_map.indexOf(a) !==
              price_category_map.lastIndexOf(a)
            ) {
              ac.push(
                new yup.ValidationError(
                  'Veuillez renseigner des tarifs différents',
                  null,
                  `quantityPerPriceCategories[${i}].priceCategory`
                )
              )
            }
            return ac
          },
          []
        )

        if (duplicateIndex) {
          return new yup.ValidationError(duplicateIndex)
        }
        return true
      }),
    bookingLimitDateInterval: yup.number(),
  })
