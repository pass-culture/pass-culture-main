import { EventStockUpdateBodyModel } from 'apiClient/v1'
import { stockEventFactory } from 'commons/utils/factories/stockEventFactories'

import { serializeStockEventEdition } from '../serializers'
import { STOCK_EVENT_FORM_DEFAULT_VALUES } from '../StockFormList/constants'
import { StockEventFormValues } from '../StockFormList/types'

vi.mock('commons/utils/date', async () => {
  return {
    ...(await vi.importActual('commons/utils/date')),
    getToday: vi.fn(() => new Date('2020-12-15T12:00:00Z')),
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
        stockId: 42,
      }),
    ]
    departementCode = '75'
  })


  it('should serialize data for stock event edition', () => {
    const expectedApiStockEvent: EventStockUpdateBodyModel = {
      id: 42,
      beginningDatetime: '2022-10-11T13:00:00Z',
      bookingLimitDatetime: '2022-10-10T21:59:59Z',
      priceCategoryId: 1,
      quantity: null,
    }

    const serializedData = serializeStockEventEdition(
      [
        ...formValuesList.map((formValues: StockEventFormValues) => ({
          ...formValues,
          stockId: 42,
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
