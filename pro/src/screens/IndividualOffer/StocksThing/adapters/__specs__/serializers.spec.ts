import { StockCreationBodyModel, StockEditionBodyModel } from 'apiClient/v1'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../../constants'
import { StockThingFormValues } from '../../types'
import { serializeStockThingList } from '../serializers'

describe('serializeStockThingList', () => {
  let formValues: StockThingFormValues
  let departementCode: string

  beforeEach(() => {
    formValues = {
      remainingQuantity: STOCK_THING_FORM_DEFAULT_VALUES.remainingQuantity,
      bookingsQuantity: STOCK_THING_FORM_DEFAULT_VALUES.bookingsQuantity,
      quantity: 12,
      bookingLimitDatetime: '2022-10-26',
      price: 10,
      activationCodesExpirationDatetime: '',
      activationCodes: [],
      isDuo: undefined,
    }
    departementCode = '75'
  })

  it('should serialize data for stock thing creation', () => {
    const expectedApiStockThing: StockCreationBodyModel = {
      bookingLimitDatetime: '2022-10-26T21:59:59Z',
      price: 10,
      quantity: 12,
    }

    const serializedData = serializeStockThingList(formValues, departementCode)
    expect(serializedData).toStrictEqual([expectedApiStockThing])
  })

  it('should fill bookingLimitDatetime with beginningDatetime when not provided', () => {
    const expectedApiStockThing: StockCreationBodyModel = {
      bookingLimitDatetime: null,
      price: 10,
      quantity: 12,
    }

    const serializedData = serializeStockThingList(
      {
        ...formValues,
        bookingLimitDatetime: '',
      },
      departementCode
    )
    expect(serializedData).toStrictEqual([expectedApiStockThing])
  })

  it('should serialize data for stock thing edition', () => {
    const expectedApiStockThing: StockEditionBodyModel = {
      id: 1,
      bookingLimitDatetime: '2022-10-26T21:59:59Z',
      price: 10,
      quantity: 12,
    }

    const serializedData = serializeStockThingList(
      {
        stockId: 1,
        ...formValues,
      },
      departementCode
    )
    expect(serializedData).toStrictEqual([expectedApiStockThing])
  })

  it('should not set null when quantity value is 0', () => {
    const serializedData = serializeStockThingList(
      {
        stockId: 1,
        ...formValues,
        quantity: 0,
      },
      departementCode
    )
    expect(serializedData[0]!.quantity).toStrictEqual(0)
  })

  it('should set null when quantity field is empty', () => {
    const serializedData = serializeStockThingList(
      {
        stockId: 1,
        ...formValues,
        quantity: null,
      },
      departementCode
    )
    // null is set in unlimited in api
    expect(serializedData[0]!.quantity).toStrictEqual(null)
  })

  it('should set null when quantity field is ""', () => {
    const serializedData = serializeStockThingList(
      {
        stockId: 1,
        ...formValues,
        quantity: '',
      },
      departementCode
    )
    // null is set in unlimited in api
    expect(serializedData[0]!.quantity).toStrictEqual(null)
  })
})
