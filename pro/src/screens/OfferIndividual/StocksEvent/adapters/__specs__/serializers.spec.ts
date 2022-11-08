import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'
import {
  IStockEventFormValues,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
} from 'components/StockEventForm'

import { serializeStockEventList } from '../serializers'

describe('screens::StockEvent::serializers:serializeStockEventList', () => {
  let formValuesList: IStockEventFormValues[]
  let departementCode: string

  beforeEach(() => {
    formValuesList = [
      {
        beginningDate: new Date('2022-10-26T00:00:00.0200'),
        beginningTime: new Date('2022-10-26T15:00:00.0200'),
        remainingQuantity: STOCK_EVENT_FORM_DEFAULT_VALUES.remainingQuantity,
        bookingsQuantity: STOCK_EVENT_FORM_DEFAULT_VALUES.bookingsQuantity,
        quantity: '12',
        bookingLimitDatetime: new Date('2022-10-26T23:00:00+0200'),
        price: '10',
        isDeletable: true,
      },
    ]
    departementCode = '75'
  })

  it('should serialize data for stock event creation', async () => {
    const expectedApiStockEvent: StockCreationBodyModel = {
      beginningDatetime: '2022-10-26T13:00:00Z',
      bookingLimitDatetime: '2022-10-26T00:00:00Z',
      price: 10,
      quantity: 12,
    }

    const serializedData = serializeStockEventList(
      formValuesList,
      departementCode
    )
    expect(serializedData).toStrictEqual([expectedApiStockEvent])
  })

  it('should serialize data for stock event without "bookingLimitDatetime"', async () => {
    const expectedApiStockEvent: StockCreationBodyModel = {
      beginningDatetime: '2022-10-26T13:00:00Z',
      bookingLimitDatetime: null,
      price: 10,
      quantity: 12,
    }

    const serializedData = serializeStockEventList(
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
      humanizedId: 'STOCK_ID',
      beginningDatetime: '2022-10-26T13:00:00Z',
      bookingLimitDatetime: '2022-10-26T00:00:00Z',
      price: 10,
      quantity: 12,
    }

    const serializedData = serializeStockEventList(
      [
        ...formValuesList.map((formValues: IStockEventFormValues) => ({
          ...formValues,
          stockId: 'STOCK_ID',
        })),
      ],
      departementCode
    )
    expect(serializedData).toStrictEqual([expectedApiStockEvent])
  })
})
