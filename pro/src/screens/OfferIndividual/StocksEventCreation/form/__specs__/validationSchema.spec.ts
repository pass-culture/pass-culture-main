import { SelectOption } from 'custom_types/form'
import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

import { RecurrenceFormValues, RecurrenceType } from '../types'
import { getValidationSchema } from '../validationSchema'

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
        endingDate: '2020-03-07',
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
        'quantityPerPriceCategories[1].quantity must be a `number` type, but the final value was: `NaN` (cast from the value `""`).',
        'Veuillez renseigner un tarif',
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
        endingDate: '2020-01-01',
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
