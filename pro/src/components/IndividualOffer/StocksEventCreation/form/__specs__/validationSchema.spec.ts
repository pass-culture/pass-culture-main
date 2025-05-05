import { addDays, addMonths } from 'date-fns'

import { SelectOption } from 'commons/custom_types/form'
import { getYupValidationSchemaErrors } from 'commons/utils/yupValidationTestHelpers'

import { weekDays } from '../constants'
import {
  DurationTypeOption,
  RecurrenceFormValues,
  RecurrenceType,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from '../types'
import { getValidationSchema, validationSchema } from '../validationSchema'

const priceCategoriesOptions: SelectOption[] = [
  { label: 'Tarif 1', value: '1' },
]

const baseValidForm: RecurrenceFormValues = {
  recurrenceType: RecurrenceType.UNIQUE,
  days: [],
  startingDate: '2050-03-03',
  endingDate: '',
  beginningTimes: ['10:00', '10:30'],
  quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
  bookingLimitDateInterval: 2,
  monthlyOption: null,
}

describe('validationSchema', () => {
  const cases: {
    description: string
    formValues: RecurrenceFormValues
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form for unique date',
      formValues: baseValidForm,
      expectedErrors: [],
    },
    {
      description: 'valid form for daily recurrence',
      formValues: {
        ...baseValidForm,
        recurrenceType: RecurrenceType.DAILY,
        endingDate: '2050-03-07',
      },
      expectedErrors: [],
    },
    {
      description: 'missing required fields for unique date',
      formValues: {
        ...baseValidForm,
        recurrenceType: RecurrenceType.UNIQUE,
        startingDate: '',
        endingDate: '',
        beginningTimes: [''],
        quantityPerPriceCategories: [
          { quantity: -5, priceCategory: '666' },
          { quantity: '', priceCategory: '' },
        ],
        bookingLimitDateInterval: '',
        monthlyOption: null,
      },
      expectedErrors: [
        'Veuillez renseigner une date',
        'Veuillez renseigner un horaire',
        '"666 " n’est pas une valeur valide de la liste',
        'Veuillez indiquer un nombre supérieur à 0',
        'Veuillez renseigner un tarif',
        'quantityPerPriceCategories[1].quantity must be a `number` type, but the final value was: `NaN` (cast from the value `""`).',
        'bookingLimitDateInterval must be a `number` type, but the final value was: `NaN` (cast from the value `""`).',
      ],
    },
    {
      description: 'missing ending date for daily recurrence',
      formValues: {
        ...baseValidForm,
        recurrenceType: RecurrenceType.DAILY,
        endingDate: '',
      },
      expectedErrors: ['Veuillez renseigner une date de fin'],
    },
    {
      description: 'missing a day value for weekly recurrence',
      formValues: {
        ...baseValidForm,
        recurrenceType: RecurrenceType.WEEKLY,
        days: [],
      },
      expectedErrors: [
        'Veuillez renseigner une date de fin',
        'Veuillez renseigner au moins un jour',
      ],
    },
    {
      description: 'duplicate hours',
      formValues: {
        ...baseValidForm,
        recurrenceType: RecurrenceType.DAILY,
        startingDate: '2050-01-01',
        endingDate: '2050-02-01',
        beginningTimes: ['10:00', '10:00'],
      },
      expectedErrors: [
        'Veuillez renseigner des horaires différents',
        'Veuillez renseigner des horaires différents',
      ],
    },
    {
      description: 'date is in the past',
      formValues: {
        ...baseValidForm,
        startingDate: '2000-01-01',
      },
      expectedErrors: ['L’évènement doit être à venir'],
    },
    {
      description: 'ending date is before starting date',
      formValues: {
        ...baseValidForm,
        recurrenceType: RecurrenceType.DAILY,
        startingDate: '2050-01-01',
        endingDate: '1999-01-01',
      },
      expectedErrors: [
        'Veuillez indiquer une date postérieure à la date de début',
      ],
    },
  ]

  cases.forEach(({ description, formValues, expectedErrors }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const errors = await getYupValidationSchemaErrors(
        getValidationSchema(priceCategoriesOptions),
        formValues
      )
      expect(errors).toEqual(expectedErrors)
    })
  })
})

describe('validationSchema with FF WIP_ENABLE_EVENT_WITH_OPENING_HOUR', () => {
  const defaultValues: StocksCalendarFormValues = {
    durationType: DurationTypeOption.ONE_DAY,
    oneDayDate: addDays(new Date(), 1).toISOString().split('T')[0],
    pricingCategoriesQuantities: [{ priceCategory: '1' }],
    specificTimeSlots: [{ slot: '00:00' }],
    timeSlotType: TimeSlotTypeOption.SPECIFIC_TIME,
    multipleDaysStartDate: addDays(new Date(), 1).toISOString().split('T')[0],
    multipleDaysEndDate: addDays(new Date(), 3).toISOString().split('T')[0],
    multipleDaysHasNoEndDate: false,
    multipleDaysWeekDays: weekDays.map((d) => ({ ...d, checked: true })),
  }

  const cases: {
    description: string
    formValues: StocksCalendarFormValues
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form for unique date',
      formValues: defaultValues,
      expectedErrors: [],
    },
    {
      description: 'invalid form for missing single day date',
      formValues: { ...defaultValues, oneDayDate: '' },
      expectedErrors: [
        'La date de l’évènement est obligatoire',
        'L’évènement doit être à venir',
        "L’évènement ne doit pas être dans plus d'un an",
      ],
    },
    {
      description: 'invalid form for single day date too far in the future',
      formValues: {
        ...defaultValues,
        oneDayDate: addMonths(new Date(), 14).toISOString().split('T')[0],
      },
      expectedErrors: ["L’évènement ne doit pas être dans plus d'un an"],
    },
    {
      description: 'invalid form for missing time slot',
      formValues: { ...defaultValues, specificTimeSlots: [{ slot: '' }] },
      expectedErrors: ['Veuillez renseigner un horaire'],
    },
    {
      description: 'invalid form for similar time slot',
      formValues: {
        ...defaultValues,
        specificTimeSlots: [{ slot: '00:00' }, { slot: '00:00' }],
      },
      expectedErrors: ['Veuillez renseigner des tarifs différents'],
    },
    {
      description: 'invalid form for invalid days before booking limit',
      formValues: {
        ...defaultValues,
        bookingLimitDateInterval: -1,
      },
      expectedErrors: ['Le nombre de jours doit être supérieur à 0'],
    },
    {
      description: 'invalid form for missing price category',
      formValues: {
        ...defaultValues,
        pricingCategoriesQuantities: [{ quantity: 12, priceCategory: '' }],
      },
      expectedErrors: ['Veuillez renseigner un tarif'],
    },
    {
      description: 'invalid form for negative quantity',
      formValues: {
        ...defaultValues,
        pricingCategoriesQuantities: [{ quantity: -1, priceCategory: '1' }],
      },
      expectedErrors: ['Veuillez indiquer un nombre supérieur à 0'],
    },
    {
      description: 'invalid form for quantity too high',
      formValues: {
        ...defaultValues,
        pricingCategoriesQuantities: [
          { quantity: 1_000_001, priceCategory: '1' },
        ],
      },
      expectedErrors: [
        'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million',
      ],
    },
    {
      description: 'invalid form for missing end date',
      formValues: {
        ...defaultValues,
        durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
        multipleDaysEndDate: '',
      },
      expectedErrors: [
        'La date de fin est obligatoire',
        'La date de fin doit être postérieure à la date de début',
        "La date de fin ne peut pas être plus d'un an après la date de début",
      ],
    },
    {
      description: 'invalid form for end date before start date',
      formValues: {
        ...defaultValues,
        durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
        multipleDaysStartDate: addDays(new Date(), 3)
          .toISOString()
          .split('T')[0],
        multipleDaysEndDate: addDays(new Date(), 1).toISOString().split('T')[0],
      },
      expectedErrors: [
        'La date de fin doit être postérieure à la date de début',
      ],
    },
    {
      description:
        'invalid form for end date more than a year after start date',
      formValues: {
        ...defaultValues,
        durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
        multipleDaysStartDate: addDays(new Date(), 1)
          .toISOString()
          .split('T')[0],
        multipleDaysEndDate: addMonths(new Date(), 13)
          .toISOString()
          .split('T')[0],
      },
      expectedErrors: [
        "La date de fin ne peut pas être plus d'un an après la date de début",
      ],
    },
    {
      description: 'invalid form for missing weekday',
      formValues: {
        ...defaultValues,
        durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
        multipleDaysWeekDays: weekDays.map((d) => ({ ...d, checked: false })),
      },
      expectedErrors: ['Sélectionnez au moins un jour de la semaine'],
    },
  ]

  cases.forEach(({ description, formValues, expectedErrors }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const errors = await getYupValidationSchemaErrors(
        validationSchema,
        formValues
      )
      expect(errors).toEqual(expectedErrors)
    })
  })
})
