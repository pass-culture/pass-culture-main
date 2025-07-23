import { addMonths, isAfter, isBefore, isSameDay } from 'date-fns'
import * as yup from 'yup'

import { getToday, isDateValid, removeTime } from 'commons/utils/date'
import { MAX_STOCKS_QUANTITY } from 'components/IndividualOffer/StocksThing/validationSchema'

import {
  DurationTypeOption,
  RecurrenceDays,
  RecurrenceType,
  TimeSlotTypeOption,
  MonthlyOption,
} from './types'

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

export const validationSchema = yup.object().shape({
  durationType: yup.string<DurationTypeOption>().required(),
  timeSlotType: yup.string<TimeSlotTypeOption>().required(),
  oneDayDate: yup.string().when('durationType', {
    is: DurationTypeOption.ONE_DAY,
    then: (schema) =>
      schema
        .required('La date de l’évènement est obligatoire')
        .test(
          'is-future',
          'L’évènement doit être à venir',
          (value) =>
            isDateValid(value) && new Date(value) >= removeTime(getToday())
        )
        .test(
          'is-not-more-than-a-year-from-now',
          "L’évènement ne doit pas être dans plus d'un an",
          (value) => new Date(value) <= addMonths(getToday(), 12)
        ),
  }),
  multipleDaysStartDate: yup.string().when('durationType', {
    is: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
    then: (schema) => schema.required('La date de début est obligatoire'),
  }),
  multipleDaysEndDate: yup.string().when('durationType', {
    is: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
    then: (schema) =>
      schema.when('multipleDaysHasNoEndDate', {
        is: false,
        then: (schema) =>
          schema
            .required('La date de fin est obligatoire')
            .test(
              'is-after-start-date',
              'La date de fin doit être postérieure à la date de début',
              function (endDate) {
                return (
                  isAfter(endDate, this.parent.multipleDaysStartDate) ||
                  isSameDay(endDate, this.parent.multipleDaysStartDate)
                )
              }
            )
            .test(
              'is-less-than-a-year-after-start-date',
              "La date de fin ne peut pas être plus d'un an après la date de début",
              function (endDate) {
                return isBefore(
                  endDate,
                  addMonths(this.parent.multipleDaysStartDate, 12)
                )
              }
            ),
      }),
  }),
  multipleDaysHasNoEndDate: yup.boolean().required(),
  multipleDaysWeekDays: yup
    .array()
    .of(
      yup.object().shape({
        checked: yup.boolean().required(),
        label: yup.string().required(),
        value: yup.string<RecurrenceDays>().required(),
      })
    )
    .when('durationType', {
      is: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
      then: (schema) =>
        schema.test(
          'at-least-one-checked',
          'Sélectionnez au moins un jour de la semaine',
          (list) => list?.some((d) => d.checked)
        ),
    })
    .required(),
  specificTimeSlots: yup
    .array()
    .required()
    .of(
      yup.object().shape({
        slot: yup.string().required('Veuillez renseigner un horaire'),
      })
    )
    .test('areSlotsUnique', function (list) {
      const slots = list.map((a) => a.slot)
      const duplicateSlotsErrors = slots
        .map((slot, i, self) => (self.indexOf(slot) !== i ? i : null))
        .filter((i) => i === 0 || Boolean(i))
        .map((index) => {
          return new yup.ValidationError(
            'Veuillez renseigner des tarifs différents',
            null,
            `specificTimeSlots[${index}].slot`
          )
        })

      if (duplicateSlotsErrors.length > 0) {
        return new yup.ValidationError(duplicateSlotsErrors)
      }

      return true
    }),
  pricingCategoriesQuantities: yup
    .array()
    .required()
    .of(
      yup.object().shape({
        priceCategory: yup.string().required('Veuillez renseigner un tarif'),
        quantity: yup
          .number()
          .transform((value) => (Number.isNaN(value) ? undefined : value))
          .min(1, 'Veuillez indiquer un nombre supérieur à 0')
          .max(
            MAX_STOCKS_QUANTITY,
            'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million'
          ),
      })
    ),
  bookingLimitDateInterval: yup
    .number()
    .transform((value) => (Number.isNaN(value) ? undefined : value))
    .min(0, 'Le nombre de jours doit être supérieur à 0'),
})
