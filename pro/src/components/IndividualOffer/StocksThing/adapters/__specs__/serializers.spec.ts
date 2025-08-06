import {
  ThingStockCreateBodyModel,
  ThingStockUpdateBodyModel,
} from '@/apiClient/v1'

import { STOCK_THING_FORM_DEFAULT_VALUES } from '../../constants'
import { StockThingFormValues } from '../../types'
import {
  serializeCreateThingStock,
  serializeUpdateThingStock,
} from '../serializers'

describe('serializeCreateThingStock', () => {
  let formValues: StockThingFormValues
  let departementCode: string
  let offerId: number

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
    offerId = 12
  })

  it('should serialize data for stock thing creation', () => {
    const expectedCreateThingStock: ThingStockCreateBodyModel = {
      bookingLimitDatetime: '2022-10-26T21:59:59Z',
      price: 10,
      quantity: 12,
      offerId: 12,
    }

    const serializedData = serializeCreateThingStock(
      formValues,
      offerId,
      departementCode
    )
    expect(serializedData).toStrictEqual(expectedCreateThingStock)
  })

  it('should fill bookingLimitDatetime with beginningDatetime when not provided', () => {
    const expectedApiStockThing: ThingStockCreateBodyModel = {
      bookingLimitDatetime: null,
      price: 10,
      quantity: 12,
      offerId: 12,
    }

    const serializedData = serializeCreateThingStock(
      {
        ...formValues,
        bookingLimitDatetime: '',
      },
      offerId,
      departementCode
    )
    expect(serializedData).toStrictEqual(expectedApiStockThing)
  })

  it('should not set null when quantity value is 0', () => {
    const serializedData = serializeCreateThingStock(
      {
        stockId: 1,
        ...formValues,
        quantity: 0,
      },
      offerId,
      departementCode
    )
    expect(serializedData.quantity).toStrictEqual(0)
  })

  it('should set undefined when quantity field is empty', () => {
    const serializedData = serializeCreateThingStock(
      {
        stockId: 1,
        ...formValues,
        quantity: undefined,
      },
      offerId,
      departementCode
    )
    // null is set in unlimited in api
    expect(serializedData.quantity).toStrictEqual(null)
  })
})

describe('serializeUpdateThingStock', () => {
  let formValues: StockThingFormValues
  let departementCode: string

  beforeEach(() => {
    formValues = {
      stockId: 42,
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
    const expectedUpdateThingStock: ThingStockUpdateBodyModel = {
      bookingLimitDatetime: '2022-10-26T21:59:59Z',
      price: 10,
      quantity: 12,
    }

    const serializedData = serializeUpdateThingStock(
      formValues,
      departementCode
    )
    expect(serializedData).toStrictEqual(expectedUpdateThingStock)
  })

  it('should fill bookingLimitDatetime with beginningDatetime when not provided', () => {
    const expectedApiStockThing: ThingStockUpdateBodyModel = {
      bookingLimitDatetime: null,
      price: 10,
      quantity: 12,
    }

    const serializedData = serializeUpdateThingStock(
      {
        ...formValues,
        bookingLimitDatetime: '',
      },
      departementCode
    )
    expect(serializedData).toStrictEqual(expectedApiStockThing)
  })

  it('should not set null when quantity value is 0', () => {
    const serializedData = serializeUpdateThingStock(
      {
        stockId: 1,
        ...formValues,
        quantity: 0,
      },
      departementCode
    )
    expect(serializedData.quantity).toStrictEqual(0)
  })

  it('should set undefined when quantity field is empty', () => {
    const serializedData = serializeUpdateThingStock(
      {
        stockId: 1,
        ...formValues,
        quantity: undefined,
      },
      departementCode
    )
    // null is set in unlimited in api
    expect(serializedData.quantity).toStrictEqual(null)
  })
})
