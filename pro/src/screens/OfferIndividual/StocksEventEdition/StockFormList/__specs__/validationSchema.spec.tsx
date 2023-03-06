import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

import { stockEventFactory } from '../stockEventFactory'
import { IStockEventFormValues } from '../types'
import { getValidationSchema } from '../validationSchema'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest.fn().mockReturnValue(new Date('2020-06-15T12:00:00Z')),
}))

describe('validationSchema', () => {
  const cases: {
    description: string
    formValues: { stocks: Partial<IStockEventFormValues>[] }
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form',
      formValues: { stocks: [stockEventFactory()] },
      expectedErrors: [],
    },
    {
      description: 'price above 300',
      formValues: { stocks: [stockEventFactory({ price: 3000 })] },
      expectedErrors: ['Veuillez renseigner un prix inférieur à 300€'],
    },
    {
      description: 'price below 0',
      formValues: { stocks: [stockEventFactory({ price: -10 })] },
      expectedErrors: ['Doit être positif'],
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
        getValidationSchema(undefined, false),
        formValues
      )
      expect(errors).toEqual(expectedErrors)
    })
  })
})
