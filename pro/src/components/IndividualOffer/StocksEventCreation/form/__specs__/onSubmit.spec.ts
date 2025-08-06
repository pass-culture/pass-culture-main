import { api } from '@/apiClient/api'
import { isError } from '@/apiClient/helpers'
import { StocksEventFactory } from '@/commons/utils/factories/individualApiFactories'

import { onSubmit } from '../onSubmit'
import {
  MonthlyOption,
  RecurrenceDays,
  RecurrenceFormValues,
  RecurrenceType,
  StocksEvent,
} from '../types'

const mockSuccessNotification = vi.fn()
const mockErrorNotification = vi.fn()

const notify = {
  success: mockSuccessNotification,
  error: mockErrorNotification,
  information: vi.fn(),
  close: vi.fn(),
}

describe('onSubmit', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2010-01-01 13:15'))
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  const cases: {
    description: string
    formValues: RecurrenceFormValues
    expectedStocks: StocksEvent[]
    expectedNotification: string
  }[] = [
    {
      description: 'generate stocks for one unique date',
      formValues: {
        recurrenceType: RecurrenceType.UNIQUE,
        days: [],
        startingDate: '2020-03-03',
        endingDate: '',
        beginningTimes: [
          { beginningTime: '10:00' },
          { beginningTime: '10:30' },
        ],
        quantityPerPriceCategories: [
          { quantity: 5, priceCategory: '1' },
          { priceCategory: '2' },
        ],
        bookingLimitDateInterval: 2,
        monthlyOption: null,
      },
      expectedStocks: [
        StocksEventFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 2,
          quantity: null,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-03-03T09:30:00Z',
          bookingLimitDatetime: '2020-03-01T09:30:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-03-03T09:30:00Z',
          bookingLimitDatetime: '2020-03-01T09:30:00Z',
          priceCategoryId: 2,
          quantity: null,
        }),
      ],
      expectedNotification: '4 nouvelles dates ont été ajoutées',
    },
    {
      description: 'generate stocks on a daily basis',
      formValues: {
        recurrenceType: RecurrenceType.DAILY,
        days: [],
        startingDate: '2020-03-03',
        endingDate: '2020-03-06',
        beginningTimes: [{ beginningTime: '10:00:00' }],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: null,
      },
      expectedStocks: [
        StocksEventFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-03-04T09:00:00Z',
          bookingLimitDatetime: '2020-03-02T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-03-05T09:00:00Z',
          bookingLimitDatetime: '2020-03-03T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-03-06T09:00:00Z',
          bookingLimitDatetime: '2020-03-04T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
      expectedNotification: '4 nouvelles dates ont été ajoutées',
    },
    {
      description: 'generate stocks on a weekly basis',
      formValues: {
        recurrenceType: RecurrenceType.WEEKLY,
        days: [RecurrenceDays.SATURDAY, RecurrenceDays.SUNDAY],
        startingDate: '2020-03-03',
        endingDate: '2020-03-20',
        beginningTimes: [{ beginningTime: '10:00' }],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: null,
      },
      expectedStocks: [
        StocksEventFactory({
          beginningDatetime: '2020-03-07T09:00:00Z',
          bookingLimitDatetime: '2020-03-05T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-03-08T09:00:00Z',
          bookingLimitDatetime: '2020-03-06T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-03-14T09:00:00Z',
          bookingLimitDatetime: '2020-03-12T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-03-15T09:00:00Z',
          bookingLimitDatetime: '2020-03-13T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
      expectedNotification: '4 nouvelles dates ont été ajoutées',
    },
    {
      description:
        'generate stocks on a monthly basis every beginning of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2020-03-03',
        endingDate: '2020-06-20',
        beginningTimes: [{ beginningTime: '10:00' }],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.X_OF_MONTH,
      },
      expectedStocks: [
        StocksEventFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-04-03T08:00:00Z',
          bookingLimitDatetime: '2020-04-01T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-05-03T08:00:00Z',
          bookingLimitDatetime: '2020-05-01T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-06-03T08:00:00Z',
          bookingLimitDatetime: '2020-06-01T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
      expectedNotification: '4 nouvelles dates ont été ajoutées',
    },
    {
      description: 'generate stocks on a monthly basis every end of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2020-03-31',
        endingDate: '2020-06-20',
        beginningTimes: [{ beginningTime: '10:00' }],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.X_OF_MONTH,
      },
      expectedStocks: [
        StocksEventFactory({
          beginningDatetime: '2020-03-31T08:00:00Z',
          bookingLimitDatetime: '2020-03-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-05-31T08:00:00Z',
          bookingLimitDatetime: '2020-05-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
      expectedNotification: '2 nouvelles dates ont été ajoutées',
    },

    {
      description:
        'generate stocks on a monthly basis by first day at beginning of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2020-03-03',
        endingDate: '2020-06-20',
        beginningTimes: [{ beginningTime: '10:00' }],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.BY_FIRST_DAY,
      },
      expectedStocks: [
        StocksEventFactory({
          beginningDatetime: '2020-03-03T09:00:00Z',
          bookingLimitDatetime: '2020-03-01T09:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-04-07T08:00:00Z',
          bookingLimitDatetime: '2020-04-05T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-05-05T08:00:00Z',
          bookingLimitDatetime: '2020-05-03T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-06-02T08:00:00Z',
          bookingLimitDatetime: '2020-05-31T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
      expectedNotification: '4 nouvelles dates ont été ajoutées',
    },
    {
      description:
        'generate stocks on a monthly basis by first day at end of month',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2020-03-31',
        endingDate: '2020-10-20',
        beginningTimes: [{ beginningTime: '10:00' }],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.BY_FIRST_DAY,
      },
      expectedStocks: [
        StocksEventFactory({
          beginningDatetime: '2020-03-31T08:00:00Z',
          bookingLimitDatetime: '2020-03-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-06-30T08:00:00Z',
          bookingLimitDatetime: '2020-06-28T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2020-09-29T08:00:00Z',
          bookingLimitDatetime: '2020-09-27T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
      expectedNotification: '3 nouvelles dates ont été ajoutées',
    },
    {
      description: 'generate stocks on a monthly basis by last day',
      formValues: {
        recurrenceType: RecurrenceType.MONTHLY,
        days: [],
        startingDate: '2023-03-31',
        endingDate: '2023-06-20',
        beginningTimes: [{ beginningTime: '10:00' }],
        quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
        bookingLimitDateInterval: 2,
        monthlyOption: MonthlyOption.BY_LAST_DAY,
      },
      expectedStocks: [
        StocksEventFactory({
          beginningDatetime: '2023-03-31T08:00:00Z',
          bookingLimitDatetime: '2023-03-29T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2023-04-28T08:00:00Z',
          bookingLimitDatetime: '2023-04-26T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
        StocksEventFactory({
          beginningDatetime: '2023-05-26T08:00:00Z',
          bookingLimitDatetime: '2023-05-24T08:00:00Z',
          priceCategoryId: 1,
          quantity: 5,
        }),
      ],
      expectedNotification: '3 nouvelles dates ont été ajoutées',
    },
  ]

  cases.forEach(
    ({ description, formValues, expectedStocks, expectedNotification }) => {
      it(`should ${description}`, async () => {
        vi.spyOn(api, 'bulkCreateEventStocks').mockResolvedValueOnce({
          stocks_count: expectedStocks.length,
        })
        await onSubmit(formValues, '75', 66, notify)

        expect(api.bulkCreateEventStocks).toBeCalledWith({
          offerId: 66,
          stocks: expectedStocks.map(
            ({
              beginningDatetime,
              bookingLimitDatetime,
              priceCategoryId,
              quantity,
            }) => ({
              beginningDatetime,
              bookingLimitDatetime,
              priceCategoryId,
              quantity,
            })
          ),
        })
        expect(mockSuccessNotification).toBeCalledWith(expectedNotification)
      })
    }
  )

  const defautFormValues = {
    recurrenceType: RecurrenceType.UNIQUE,
    days: [],
    startingDate: '2020-03-03',
    endingDate: '',
    beginningTimes: [{ beginningTime: '10:00' }, { beginningTime: '10:30' }],
    quantityPerPriceCategories: [
      { quantity: 5, priceCategory: '1' },
      { priceCategory: '2' },
    ],
    bookingLimitDateInterval: 2,
    monthlyOption: null,
  }

  const errorCases = [
    {
      errorMessage: 'Starting date is empty',
      formValues: {
        ...defautFormValues,
        startingDate: '2020-03-033',
      },
    },
    {
      errorMessage: 'Starting or ending date is empty',
      formValues: {
        ...defautFormValues,
        recurrenceType: RecurrenceType.DAILY,
        endingDate: '',
      },
    },
    {
      errorMessage: 'Starting, ending date or days is empty',
      formValues: {
        ...defautFormValues,
        recurrenceType: RecurrenceType.WEEKLY,
        days: [],
      },
    },
    {
      errorMessage: 'Starting or ending date is empty',
      formValues: {
        ...defautFormValues,
        recurrenceType: RecurrenceType.MONTHLY,
        startingDate: '',
      },
    },
    {
      errorMessage: 'Starting or ending date is empty',
      formValues: {
        ...defautFormValues,
        recurrenceType: RecurrenceType.MONTHLY,
        endingDate: '',
      },
    },
    {
      errorMessage: 'Monthly option is empty',
      formValues: {
        ...defautFormValues,
        recurrenceType: RecurrenceType.MONTHLY,
        endingDate: '2020-03-10',
        monthlyOption: null,
      },
    },
  ]

  errorCases.forEach(({ errorMessage, formValues }) =>
    it(`should raise error if ${errorMessage}`, async () => {
      try {
        await onSubmit(formValues, '75', 66, notify)
      } catch (error) {
        expect(isError(error)).toBeTruthy()
        if (isError(error)) {
          expect(error.message).toBe(errorMessage)
        }
      }
    })
  )

  it(`should create nothing when creation limit is reach`, async () => {
    const formValues = {
      recurrenceType: RecurrenceType.MONTHLY,
      days: [],
      startingDate: '2020-03-03',
      endingDate: '2023-07-20',
      beginningTimes: [{ beginningTime: '08:00' }],
      quantityPerPriceCategories: [{ quantity: 5, priceCategory: '1' }],
      bookingLimitDateInterval: 2,
      monthlyOption: MonthlyOption.BY_FIRST_DAY,
    }

    vi.spyOn(api, 'bulkCreateEventStocks').mockRejectedValueOnce({
      stocks: ['Erreur'],
    })

    const result = await onSubmit(formValues, '75', 66, notify)

    expect(mockErrorNotification).toHaveBeenCalledWith(
      `Une erreur est survenue lors de l’enregistrement de vos stocks.`
    )
    expect(result).toEqual(undefined)
  })
})
