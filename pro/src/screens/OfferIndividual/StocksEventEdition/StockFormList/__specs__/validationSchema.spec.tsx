import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

import { stockEventFactory } from '../stockEventFactory'
import { StockEventFormValues } from '../types'
import { getValidationSchema } from '../validationSchema'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest.fn().mockReturnValue(new Date('2020-06-15T12:00:00Z')),
}))

describe('validationSchema', () => {
  const cases: {
    description: string
    formValues: { stocks: Partial<StockEventFormValues>[] }
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form',
      formValues: { stocks: [stockEventFactory()] },
      expectedErrors: [],
    },
    {
      description: 'bad quantity',
      formValues: { stocks: [stockEventFactory({ remainingQuantity: -10 })] },
      expectedErrors: ['Doit être positif'],
    },
    {
      description: 'beginning date in the past',
      formValues: {
        stocks: [
          stockEventFactory({
            beginningDate: new Date('2019-06-15T12:00:00Z'),
            bookingLimitDatetime: new Date('2019-05-15T12:00:00Z'),
          }),
        ],
      },
      expectedErrors: ['L’évènement doit être à venir'],
    },
    {
      description: 'beginning date in the past',
      formValues: {
        stocks: [
          stockEventFactory({
            beginningDate: new Date('2022-06-15T12:00:00Z'),
            bookingLimitDatetime: new Date('2023-05-15T12:00:00Z'),
          }),
        ],
      },
      expectedErrors: [
        'Veuillez renseigner une date antérieure à la date de l’évènement',
      ],
    },
  ]

  cases.forEach(({ description, formValues, expectedErrors }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const errors = await getYupValidationSchemaErrors(
        getValidationSchema([{ value: '1', label: 'Categorie 1' }]),
        formValues
      )
      expect(errors).toEqual(expectedErrors)
    })
  })
})
