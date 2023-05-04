import { SelectOption } from 'custom_types/form'
import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

import { RecurrenceFormValues, RecurrenceType } from '../types'
import { getValidationSchema } from '../validationSchema'

const priceCategoriesOptions: SelectOption[] = [
  { label: 'Tarif 1', value: '1' },
]

const baseValidForm: RecurrenceFormValues = {
  recurrenceType: RecurrenceType.UNIQUE,
  startingDate: new Date('2020-03-03'),
  endingDate: null,
  beginningTimes: [
    new Date('2020-01-01T10:00:00'),
    new Date('2020-01-01T10:30:00'),
  ],
  quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
  bookingLimitDateInterval: 2,
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
        endingDate: new Date('2020-03-07'),
      },
      expectedErrors: [],
    },
    {
      description: 'missing required fields for unique date',
      formValues: {
        recurrenceType: '',
        startingDate: null,
        endingDate: null,
        beginningTimes: [null],
        quantityPerPriceCategories: [
          { quantity: -5, priceCategory: '666' },
          { quantity: '', priceCategory: '' },
        ],
        bookingLimitDateInterval: '',
      },
      expectedErrors: [
        'recurrenceType must be one of the following values: UNIQUE, DAILY, WEEKLY, MONTHLY',
        'Veuillez renseigner une date de début',
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
        endingDate: null,
      },
      expectedErrors: ['Veuillez renseigner une date de fin'],
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
