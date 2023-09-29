import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { individualStockEventListFactory } from 'utils/individualApiFactories'

import { onSubmit } from '../onSubmit'
import {
  MonthlyOption,
  RecurrenceDays,
  RecurrenceFormValues,
  RecurrenceType,
} from '../types'

vi.mock('uuid', () => ({ v4: () => 'uuid' }))

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
        startingDate: '2020-03-03',
        endingDate: '',
        beginningTimes: ['10:00', '10:30'],
        quantityPerPriceCategories: [
          { quantity: 5, priceCategory: '1' },
          { quantity: '', priceCategory: '2' },
        ],
        bookingLimitDateInterval: 2,
        monthlyOption: null,
      },
      expectedStocks: [
        individualStockEventListFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 2,
          quantity: null,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-03-03T09:30:00Z',
          bookingLimitDatetime: '2020-03-01T09:30:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-03-03T09:30:00Z',
          bookingLimitDatetime: '2020-03-01T09:30:00Z',
          priceCategoryId: 2,
          quantity: null,
        }),
      ],
    },
    {
      description: 'generate stocks on a daily basis',
      formValues: {
        recurrenceType: RecurrenceType.DAILY,
        days: [],
        startingDate: '2020-03-03',
        endingDate: '2020-03-06',
        beginningTimes: ['10:00:00'],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: null,
      },
      expectedStocks: [
        individualStockEventListFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-03-04T09:00:00Z',
          bookingLimitDatetime: '2020-03-02T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-03-05T09:00:00Z',
          bookingLimitDatetime: '2020-03-03T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-03-06T09:00:00Z',
          bookingLimitDatetime: '2020-03-04T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
    },
    {
      description: 'generate stocks on a weekly basis',
      formValues: {
        recurrenceType: RecurrenceType.WEEKLY,
        days: [RecurrenceDays.SATURDAY, RecurrenceDays.SUNDAY],
        startingDate: '2020-03-03',
        endingDate: '2020-03-20',
        beginningTimes: ['10:00'],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: null,
      },
      expectedStocks: [
        individualStockEventListFactory({
          beginningDatetime: '2020-03-07T09:00:00Z',
          bookingLimitDatetime: '2020-03-05T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-03-08T09:00:00Z',
          bookingLimitDatetime: '2020-03-06T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-03-14T09:00:00Z',
          bookingLimitDatetime: '2020-03-12T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-03-15T09:00:00Z',
          bookingLimitDatetime: '2020-03-13T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
    },
    {
      description:
        'generate stocks on a monthly basis every beginning of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2020-03-03',
        endingDate: '2020-06-20',
        beginningTimes: ['10:00'],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.X_OF_MONTH,
      },
      expectedStocks: [
        individualStockEventListFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-04-03T08:00:00Z',
          bookingLimitDatetime: '2020-04-01T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-05-03T08:00:00Z',
          bookingLimitDatetime: '2020-05-01T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-06-03T08:00:00Z',
          bookingLimitDatetime: '2020-06-01T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
    },
    {
      description: 'generate stocks on a monthly basis every end of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2020-03-31',
        endingDate: '2020-06-20',
        beginningTimes: ['10:00'],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.X_OF_MONTH,
      },
      expectedStocks: [
        individualStockEventListFactory({
          beginningDatetime: '2020-03-31T08:00:00Z',
          bookingLimitDatetime: '2020-03-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-05-31T08:00:00Z',
          bookingLimitDatetime: '2020-05-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
    },

    {
      description:
        'generate stocks on a monthly basis by first day at beginning of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2020-03-03',
        endingDate: '2020-06-20',
        beginningTimes: ['10:00'],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.BY_FIRST_DAY,
      },
      expectedStocks: [
        individualStockEventListFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-04-07T08:00:00Z',
          bookingLimitDatetime: '2020-04-05T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-05-05T08:00:00Z',
          bookingLimitDatetime: '2020-05-03T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-06-02T08:00:00Z',
          bookingLimitDatetime: '2020-05-31T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
    },
    {
      description:
        'generate stocks on a monthly basis by first day at end of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2020-03-31',
        endingDate: '2020-10-20',
        beginningTimes: ['10:00'],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.BY_FIRST_DAY,
      },
      expectedStocks: [
        individualStockEventListFactory({
          beginningDatetime: '2020-03-31T08:00:00Z',
          bookingLimitDatetime: '2020-03-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-06-30T08:00:00Z',
          bookingLimitDatetime: '2020-06-28T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2020-09-29T08:00:00Z',
          bookingLimitDatetime: '2020-09-27T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
    },
    {
      description: 'generate stocks on a monthly basis by last day',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2023-03-31',
        endingDate: '2023-06-20',
        beginningTimes: ['10:00'],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.BY_LAST_DAY,
      },
      expectedStocks: [
        individualStockEventListFactory({
          beginningDatetime: '2023-03-31T08:00:00Z',
          bookingLimitDatetime: '2023-03-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2023-04-28T08:00:00Z',
          bookingLimitDatetime: '2023-04-26T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        individualStockEventListFactory({
          beginningDatetime: '2023-05-26T08:00:00Z',
          bookingLimitDatetime: '2023-05-24T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
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
