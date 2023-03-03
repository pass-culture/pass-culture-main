import { IStocksEvent } from 'components/StocksEventList/StocksEventList'

import { onSubmit } from '../onSubmit'
import { RecurrenceFormValues, RecurrenceType } from '../types'

describe('onSubmit', () => {
  const cases: {
    description: string
    formValues: RecurrenceFormValues
    expectedStocks: IStocksEvent[]
  }[] = [
    {
      description: 'one unique date',
      formValues: {
        recurrenceType: RecurrenceType.UNIQUE,
        startingDate: new Date('2020-03-03'),
        beginningTimes: [
          new Date('2020-01-01T10:00:00'),
          new Date('2020-01-01T10:30:00'),
        ],
        quantityPerPriceCategories: [
          { quantity: 5, priceCategory: '1' },
          { quantity: '', priceCategory: '2' },
        ],
        bookingLimitDateInterval: 2,
      },
      expectedStocks: [
        {
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 2,
          quantity: null,
        },
        {
          beginningDatetime: '2020-03-03T09:30:00Z',
          bookingLimitDatetime: '2020-03-01T09:30:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-03-03T09:30:00Z',
          bookingLimitDatetime: '2020-03-01T09:30:00Z',
          priceCategoryId: 2,
          quantity: null,
        },
      ],
    },
  ]

  cases.forEach(({ description, formValues, expectedStocks }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const newStocks = onSubmit(formValues, '75')

      expect(newStocks).toEqual(expectedStocks)
    })
  })
})
