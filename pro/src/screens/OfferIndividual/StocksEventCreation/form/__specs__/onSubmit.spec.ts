import { StocksEvent } from 'components/StocksEventList/StocksEventList'

import { onSubmit } from '../onSubmit'
import { RecurrenceFormValues, RecurrenceType } from '../types'

describe('onSubmit', () => {
  const cases: {
    description: string
    formValues: RecurrenceFormValues
    expectedStocks: StocksEvent[]
  }[] = [
    {
      description: 'generate stocks for one unique date',
      formValues: {
        recurrenceType: RecurrenceType.UNIQUE,
        days: [],
        startingDate: new Date('2020-03-03'),
        endingDate: null,
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
    {
      description: 'generate stocks on a daily basis',
      formValues: {
        recurrenceType: RecurrenceType.DAILY,
        days: [],
        startingDate: new Date('2020-03-03'),
        endingDate: new Date('2020-03-06'),
        beginningTimes: [new Date('2020-01-01T10:00:00')],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
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
          beginningDatetime: '2020-03-04T09:00:00Z',
          bookingLimitDatetime: '2020-03-02T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-03-05T09:00:00Z',
          bookingLimitDatetime: '2020-03-03T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-03-06T09:00:00Z',
          bookingLimitDatetime: '2020-03-04T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
      ],
    },
  ]

  cases.forEach(({ description, formValues, expectedStocks }) => {
    it(`should ${description}`, async () => {
      const newStocks = onSubmit(formValues, '75')

      expect(newStocks).toEqual(expectedStocks)
    })
  })
})
