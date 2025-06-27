import { stockEventFactory } from 'commons/utils/factories/stockEventFactories'
import { getYupValidationSchemaErrors } from 'commons/utils/yupValidationTestHelpers'

import { StockEventFormValues } from '../types'
import { getValidationSchema } from '../validationSchema'

vi.mock('commons/utils/date', async () => {
  return {
    ...(await vi.importActual('commons/utils/date')),
    getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
  }
})

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
            beginningDate: '2019-06-15',
            bookingLimitDatetime: '2019-05-15',
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
            beginningDate: '2022-06-15',
            bookingLimitDatetime: '2023-05-15',
          }),
        ],
      },
      expectedErrors: [
        'Veuillez renseigner une date antérieure à la date de l’évènement',
      ],
    },
    {
      description: 'beginning date is empty',
      formValues: {
        stocks: [
          stockEventFactory({
            beginningDate: '',
          }),
        ],
      },
      expectedErrors: [],
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
