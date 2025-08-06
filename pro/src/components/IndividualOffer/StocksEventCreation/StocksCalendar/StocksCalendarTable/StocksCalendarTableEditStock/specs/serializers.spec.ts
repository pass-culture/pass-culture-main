import { EventStockUpdateBodyModel } from '@/apiClient//v1'
import { getOfferStockFactory } from '@/commons/utils/factories/individualApiFactories'

import { EditStockFormValues } from '../StocksCalendarTableEditStock'
import { serializeStockFormValuesForUpdate } from '../serializers'

describe('serializeStockFormValuesForUpdate', () => {
  let formValues: EditStockFormValues
  let departementCode: string
  let stockId: number

  beforeEach(() => {
    formValues = {
      date: '2022-10-11',
      time: '13:00:00',
      priceCategory: '1',
      bookingLimitDate: '2022-10-10',
      remainingQuantity: 17,
    }
    departementCode = '75'
    stockId = 42
  })

  it('should serialize data for stock event edition', () => {
    const serializedData = serializeStockFormValuesForUpdate(
      getOfferStockFactory({ id: stockId }),
      formValues,
      departementCode
    )

    const expectedApiStockEvent: EventStockUpdateBodyModel = {
      id: stockId,
      beginningDatetime: '2022-10-11T11:00:00Z',
      bookingLimitDatetime: '2022-10-10T11:00:00Z',
      priceCategoryId: 1,
      quantity: 17,
    }
    expect(serializedData).toStrictEqual(expectedApiStockEvent)
  })

  it('should serialize data for stock event edition with unlimited stock', () => {
    const serializedData = serializeStockFormValuesForUpdate(
      getOfferStockFactory({ id: stockId }),
      { ...formValues, remainingQuantity: undefined },
      departementCode
    )

    const expectedApiStockEvent: EventStockUpdateBodyModel = {
      id: stockId,
      beginningDatetime: '2022-10-11T11:00:00Z',
      bookingLimitDatetime: '2022-10-10T11:00:00Z',
      priceCategoryId: 1,
      quantity: null,
    }
    expect(serializedData).toStrictEqual(expectedApiStockEvent)
  })

  it('should serialize data for stock event edition with 0 stock', () => {
    const serializedData = serializeStockFormValuesForUpdate(
      getOfferStockFactory({ id: stockId }),
      { ...formValues, remainingQuantity: 0 },
      departementCode
    )

    const expectedApiStockEvent: EventStockUpdateBodyModel = {
      id: stockId,
      beginningDatetime: '2022-10-11T11:00:00Z',
      bookingLimitDatetime: '2022-10-10T11:00:00Z',
      priceCategoryId: 1,
      quantity: 0,
    }
    expect(serializedData).toStrictEqual(expectedApiStockEvent)
  })

  it('should serialize data for stock event edition with bookings', () => {
    const serializedData = serializeStockFormValuesForUpdate(
      getOfferStockFactory({ id: stockId, bookingsQuantity: 22 }),
      { ...formValues, remainingQuantity: 100 },
      departementCode
    )

    expect(serializedData).toEqual(expect.objectContaining({ quantity: 122 }))
  })
})
