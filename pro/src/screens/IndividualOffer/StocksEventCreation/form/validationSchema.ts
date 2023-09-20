import * as yup from 'yup'

import { oneOfSelectOption } from 'core/shared/utils/validation'
import { SelectOption } from 'custom_types/form'
import { MAX_STOCKS_QUANTITY } from 'screens/IndividualOffer/StocksThing/validationSchema'
import { getToday, isDateValid, removeTime } from 'utils/date'

import { RecurrenceType } from './types'

export const getValidationSchema = (priceCategoriesOptions: SelectOption[]) =>
  yup.object().shape({
    recurrenceType: yup
      .string()
      .required()
      .oneOf(Object.values(RecurrenceType)),
    startingDate: yup
      .string()
      .transform((curr, orig) => (orig === '' ? null : curr))
      .nullable()
      .test(
        'is-future',
        'L’évènement doit être à venir',
        value => isDateValid(value) && new Date(value) > removeTime(getToday())
      )
      .when('recurrenceType', {
        is: RecurrenceType.UNIQUE,
        then: schema => schema.required('Veuillez renseigner une date'),
        otherwise: schema =>
          schema.required('Veuillez renseigner une date de début'),
      }),
    endingDate: yup
      .string()
      .transform((curr, orig) => (orig === '' ? null : curr))
      .nullable('Veuillez renseigner une date de fin')
      .when('recurrenceType', {
        is: (recurrenceType: RecurrenceType) =>
          recurrenceType !== RecurrenceType.UNIQUE,
        then: schema =>
          schema
            .required('Veuillez renseigner une date de fin')
            .test(
              'is-after-starting-date',
              'Veuillez indiquer une date postérieure à la date de début',
              function (value) {
                const startingDate = this.parent.startingDate

                return (
                  isDateValid(startingDate) &&
                  isDateValid(value) &&
                  new Date(value) > new Date(startingDate)
                )
              }
            ),
      }),
    days: yup
      .array()
      .of(yup.string())
      .when('recurrenceType', {
        is: RecurrenceType.WEEKLY,
        then: schema => schema.min(1, 'Veuillez renseigner au moins un jour'),
      }),
    beginningTimes: yup
      .array()
      .of(yup.string().nullable().required('Veuillez renseigner un horaire'))
      .test('arebeginningTimesUnique', function (list) {
        if (!list) {
          return
        }
        const beginningTimesMap = [...list]
        const duplicateIndex = beginningTimesMap.reduce<yup.ValidationError[]>(
          (accumulator, currentValue, index) => {
            if (
              beginningTimesMap.indexOf(currentValue) !==
              beginningTimesMap.lastIndexOf(currentValue)
            ) {
              accumulator.push(
                new yup.ValidationError(
                  'Veuillez renseigner des horaires différents',
                  null,
                  `beginningTimes[${index}]`
                )
              )
            }
            return accumulator
          },
          []
        )

        if (duplicateIndex) {
          return new yup.ValidationError(duplicateIndex)
        }
        return true
      }),
    quantityPerPriceCategories: yup
      .array()
      .of(
        yup.object().shape({
          quantity: yup
            .number()
            .nullable()
            .min(1, 'Veuillez indiquer un nombre supérieur à 0')
            .max(
              MAX_STOCKS_QUANTITY,
              'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million'
            ),
          priceCategory: oneOfSelectOption(
            yup.string().required('Veuillez renseigner un tarif'),
            priceCategoriesOptions
          ),
        })
      )
      .test('isPriceCategoryUnique', function (list) {
        if (!list) {
          return
        }
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
    monthlyOption: yup
      .string()
      .nullable()
      .when('recurrenceType', {
        is: RecurrenceType.MONTHLY,
        then: schema => schema.required('Veuillez choisir une option'),
      }),
  })
