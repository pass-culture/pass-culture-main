import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import {
  IStockEventFormValues,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
} from 'screens/OfferIndividual/StocksEventEdition/StockFormList'
import { stockEventFactory } from 'screens/OfferIndividual/StocksEventEdition/StockFormList/stockEventFactory'

import { serializeStockEventEdition } from '../serializers'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2022-09-26T13:00:00Z')),
}))

describe('screens::StockEvent::serializers:serializeStockEventEdition', () => {
  let formValuesList: IStockEventFormValues[]
  let departementCode: string

  beforeEach(() => {
    formValuesList = [
      stockEventFactory({
        beginningDate: new Date('2022-10-26T00:00:00.0200'),
        beginningTime: new Date('2022-10-26T15:00:00.0200'),
        remainingQuantity: STOCK_EVENT_FORM_DEFAULT_VALUES.remainingQuantity,
        bookingsQuantity: STOCK_EVENT_FORM_DEFAULT_VALUES.bookingsQuantity,
        bookingLimitDatetime: new Date('2022-10-26T00:00:00'),
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
        ...formValuesList.map((formValues: IStockEventFormValues) => ({
          ...formValues,
          bookingLimitDatetime: null,
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
        ...formValuesList.map((formValues: IStockEventFormValues) => ({
          ...formValues,
          stockId: 1,
          beginningDate: new Date('2022-10-11T00:00:00.0200'),
          beginningTime: new Date('2022-10-11T15:00:00.0200'),
          bookingLimitDatetime: new Date('2022-10-10T00:00:00'),
          priceCategoryId: '1',
        })),
      ],
      departementCode
    )
    expect(serializedData).toStrictEqual([expectedApiStockEvent])
  })
})
