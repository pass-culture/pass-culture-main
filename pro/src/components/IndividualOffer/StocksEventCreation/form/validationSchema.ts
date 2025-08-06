import * as yup from 'yup'

import { getToday, isDateValid, removeTime } from 'commons/utils/date'
import { MAX_STOCKS_QUANTITY } from 'components/IndividualOffer/StocksThing/validationSchema'

import { MonthlyOption, RecurrenceDays, RecurrenceType } from './types'

export const getValidationSchema = () =>
  yup.object().shape({
    recurrenceType: yup
      .string()
      .required()
      .oneOf(Object.values(RecurrenceType)),
    startingDate: yup
      .string()
      .required()
      .transform((curr, orig) => (orig === '' ? null : curr))
      .nullable()
      .test(
        'is-future',
        'L’évènement doit être à venir',
        (value) =>
          isDateValid(value) && new Date(value) > removeTime(getToday())
      )
      .when('recurrenceType', {
        is: RecurrenceType.UNIQUE,
        then: (schema) => schema.required('Veuillez renseigner une date'),
        otherwise: (schema) =>
          schema.required('Veuillez renseigner une date de début'),
      }),
    endingDate: yup
      .string()
      .transform((curr, orig) => (orig === '' ? null : curr))
      .nullable()
      .when('recurrenceType', {
        is: (recurrenceType: RecurrenceType) =>
          recurrenceType !== RecurrenceType.UNIQUE,
        then: (schema) =>
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
      .required()
      .of(yup.string<RecurrenceDays>().defined())
      .when('recurrenceType', {
        is: RecurrenceType.WEEKLY,
        then: (schema) => schema.min(1, 'Veuillez renseigner au moins un jour'),
      }),
    beginningTimes: yup
      .array()
      .required()
      .of(
        yup.object({
          beginningTime: yup
            .string()
            .required('Veuillez renseigner un horaire'),
        })
      )
      // TODO(cnormant, 2025-07-23): create and use a custom test, its certainly not the only place where we need to check for duplicate values
      .test('arebeginningTimesUnique', (list) => {
        const duplicateIndex = list
          .map((time) => time.beginningTime)
          .reduce<yup.ValidationError[]>(
            (accumulator, currentValue, index, self) => {
              if (
                self.indexOf(currentValue) !== self.lastIndexOf(currentValue)
              ) {
                accumulator.push(
                  new yup.ValidationError(
                    'Veuillez renseigner des horaires différents',
                    null,
                    `beginningTimes[${index}].beginningTime`
                  )
                )
              }
              return accumulator
            },
            []
          )

        if (duplicateIndex.length > 0) {
          return new yup.ValidationError(duplicateIndex)
        }
        return true
      }),
    quantityPerPriceCategories: yup
      .array()
      .required()
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
          priceCategory: yup.string().required('Veuillez renseigner un tarif'),
        })
      )
      .test('isPriceCategoryUnique', function (list) {
        const price_category_map = list.map((a) => a.priceCategory)
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

        if (duplicateIndex.length > 0) {
          return new yup.ValidationError(duplicateIndex)
        }
        return true
      }),
    bookingLimitDateInterval: yup.number().required().nullable(),
    monthlyOption: yup
      .string<MonthlyOption>()
      .nullable()
      .when('recurrenceType', {
        is: RecurrenceType.MONTHLY,
        then: (schema) => schema.required('Veuillez choisir une option'),
      }),
  })
