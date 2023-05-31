import { StocksEvent } from 'components/StocksEventList/StocksEventList'

import { onSubmit } from '../onSubmit'
import {
  MonthlyOption,
  RecurrenceDays,
  RecurrenceFormValues,
  RecurrenceType,
} from '../types'

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
        monthlyOption: null,
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
        monthlyOption: null,
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
    {
      description: 'generate stocks on a weekly basis',
      formValues: {
        recurrenceType: RecurrenceType.WEEKLY,
        days: [RecurrenceDays.SATURDAY, RecurrenceDays.SUNDAY],
        startingDate: new Date('2020-03-03'),
        endingDate: new Date('2020-03-20'),
        beginningTimes: [new Date('2020-01-01T10:00:00')],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: null,
      },
      expectedStocks: [
        {
          beginningDatetime: '2020-03-07T09:00:00Z',
          bookingLimitDatetime: '2020-03-05T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-03-08T09:00:00Z',
          bookingLimitDatetime: '2020-03-06T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-03-14T09:00:00Z',
          bookingLimitDatetime: '2020-03-12T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-03-15T09:00:00Z',
          bookingLimitDatetime: '2020-03-13T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
      ],
    },
    {
      description:
        'generate stocks on a monthly basis every beginning of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: new Date('2020-03-03'),
        endingDate: new Date('2020-06-20'),
        beginningTimes: [new Date('2020-01-01T10:00:00')],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.X_OF_MONTH,
      },
      expectedStocks: [
        {
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-04-03T08:00:00Z',
          bookingLimitDatetime: '2020-04-01T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-05-03T08:00:00Z',
          bookingLimitDatetime: '2020-05-01T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-06-03T08:00:00Z',
          bookingLimitDatetime: '2020-06-01T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
      ],
    },
    {
      description: 'generate stocks on a monthly basis every end of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: new Date('2020-03-31'),
        endingDate: new Date('2020-06-20'),
        beginningTimes: [new Date('2020-01-01T10:00:00')],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.X_OF_MONTH,
      },
      expectedStocks: [
        {
          beginningDatetime: '2020-03-31T08:00:00Z',
          bookingLimitDatetime: '2020-03-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-05-31T08:00:00Z',
          bookingLimitDatetime: '2020-05-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
      ],
    },

    {
      description:
        'generate stocks on a monthly basis by first day at beginning of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: new Date('2020-03-03'),
        endingDate: new Date('2020-06-20'),
        beginningTimes: [new Date('2020-01-01T10:00:00')],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.BY_FIRST_DAY,
      },
      expectedStocks: [
        {
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-04-07T08:00:00Z',
          bookingLimitDatetime: '2020-04-05T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-05-05T08:00:00Z',
          bookingLimitDatetime: '2020-05-03T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-06-02T08:00:00Z',
          bookingLimitDatetime: '2020-05-31T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
      ],
    },
    {
      description:
        'generate stocks on a monthly basis by first day at end of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: new Date('2020-03-31'),
        endingDate: new Date('2020-10-20'),
        beginningTimes: [new Date('2020-01-01T10:00:00')],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.BY_FIRST_DAY,
      },
      expectedStocks: [
        {
          beginningDatetime: '2020-03-31T08:00:00Z',
          bookingLimitDatetime: '2020-03-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-06-30T08:00:00Z',
          bookingLimitDatetime: '2020-06-28T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2020-09-29T08:00:00Z',
          bookingLimitDatetime: '2020-09-27T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
      ],
    },
    {
      description: 'generate stocks on a monthly basis by last day',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: new Date('2023-03-31'),
        endingDate: new Date('2023-06-20'),
        beginningTimes: [new Date('2020-01-01T10:00:00')],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.BY_LAST_DAY,
      },
      expectedStocks: [
        {
          beginningDatetime: '2023-03-31T08:00:00Z',
          bookingLimitDatetime: '2023-03-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2023-04-28T08:00:00Z',
          bookingLimitDatetime: '2023-04-26T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        },
        {
          beginningDatetime: '2023-05-26T08:00:00Z',
          bookingLimitDatetime: '2023-05-24T08:00:00Z',
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
