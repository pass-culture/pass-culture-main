import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import {
  StockEventFormValues,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
} from 'screens/OfferIndividual/StocksEventEdition/StockFormList'
import { stockEventFactory } from 'screens/OfferIndividual/StocksEventEdition/StockFormList/stockEventFactory'

import { serializeStockEventEdition } from '../serializers'

vi.mock('utils/date', async () => {
  const actual = (await vi.importActual('utils/date')) || {}
  return {
    ...actual,
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

describe('serializeStockEventEdition', () => {
  let formValuesList: StockEventFormValues[]
  let departementCode: string

  beforeEach(() => {
    formValuesList = [
      stockEventFactory({
        beginningDate: '2022-10-26',
        beginningTime: '15:00',
        remainingQuantity: STOCK_EVENT_FORM_DEFAULT_VALUES.remainingQuantity,
        bookingsQuantity: STOCK_EVENT_FORM_DEFAULT_VALUES.bookingsQuantity,
        bookingLimitDatetime: '2022-10-26',
        isDeletable: true,
        readOnlyFields: [],
        stockId: undefined,
      }),
    ]
    departementCode = '75'
  })

  it('should serialize data for stock event creation', async () => {
    const expectedApiStockEvent: StockCreationBodyModel = {
      beginningDatetime: '2022-10-26T13:00:00Z',
      bookingLimitDatetime: '2022-10-26T13:00:00Z',
      priceCategoryId: 1,
      quantity: null,
    }

    const serializedData = serializeStockEventEdition(
      formValuesList,
      departementCode
    )
    expect(serializedData).toStrictEqual([expectedApiStockEvent])
  })

  it('should serialize data for stock event with "bookingLimitDatetime" even if not provided', async () => {
    const expectedApiStockEvent: StockCreationBodyModel = {
      beginningDatetime: '2022-10-26T13:00:00Z',
      bookingLimitDatetime: '2022-10-26T13:00:00Z',
      priceCategoryId: 1,
      quantity: null,
    }

    const serializedData = serializeStockEventEdition(
      [
        ...formValuesList.map((formValues: StockEventFormValues) => ({
          ...formValues,
          bookingLimitDatetime: '',
        })),
      ],
      departementCode
    )
    expect(serializedData).toStrictEqual([expectedApiStockEvent])
  })

  it('should serialize data for stock event edition', async () => {
    const expectedApiStockEvent: StockEditionBodyModel = {
      id: 1,
      beginningDatetime: '2022-10-11T13:00:00Z',
      bookingLimitDatetime: '2022-10-10T21:59:59Z',
      priceCategoryId: 1,
      quantity: null,
    }

    const serializedData = serializeStockEventEdition(
      [
        ...formValuesList.map((formValues: StockEventFormValues) => ({
          ...formValues,
          stockId: 1,
          beginningDate: '2022-10-11',
          beginningTime: '15:00',
          bookingLimitDatetime: '2022-10-10',
          priceCategoryId: '1',
        })),
      ],
      departementCode
    )
    expect(serializedData).toStrictEqual([expectedApiStockEvent])
  })
})
