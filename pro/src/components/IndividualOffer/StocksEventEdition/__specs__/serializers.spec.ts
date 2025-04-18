import { EventStockUpdateBodyModel } from 'apiClient/v1'
import { stockEventFactory } from 'commons/utils/factories/stockEventFactories'

import { serializeStockEventEdition, serializeBookingLimitDatetime, buildDateTime } from '../serializers'
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
  
  it('should throw error', () => {
    expect(() => serializeStockEventEdition(
      [
        ...formValuesList.map((formValues: StockEventFormValues) => ({
          ...formValues,
          priceCategoryId: '',
        })),
      ],
      departementCode
    )).toThrowError('Le tarif est invalide')

    expect(() => serializeStockEventEdition(
      [
        ...formValuesList.map((formValues: StockEventFormValues) => ({
          ...formValues,
          beginningTime: '',
        })),
      ],
      departementCode
    )).toThrowError("L'heure de début d'évenement est invalide")

    expect(() => serializeStockEventEdition(
      [
        ...formValuesList.map((formValues: StockEventFormValues) => ({
          ...formValues,
          beginningDate: '20',
        })),
      ],
      departementCode
    )).toThrowError("La date ou l’heure est invalide")

    expect(() => serializeStockEventEdition(
      [
        ...formValuesList.map((formValues: StockEventFormValues) => ({
          ...formValues,
          beginningDate: '',
          beginningTime: '',
        })),
      ],
      departementCode
    )).toThrowError("La date de début d'évenement est invalide")
  })
})

describe('serializeBookingLimitDatetime', () => {
  it('should serialize booking limit datetime when beginningDatetime and bookingLimitDatetime are on the same date', () => {
    const serializedBookingLimitDatetime = serializeBookingLimitDatetime('2022-10-11', '13:00', '2022-10-11T14:00:00', '75')
    expect(serializedBookingLimitDatetime).toStrictEqual('2022-10-11T11:00:00Z')
  })

  it('should serialize booking limit datetime', () => {
    const serializedBookingLimitDatetime = serializeBookingLimitDatetime('2022-10-11', '13:00', '2022-10-13T14:00:00', '75')
    expect(serializedBookingLimitDatetime).toStrictEqual('2022-10-13T21:59:59Z')
  })
})

describe('buildDateTime', () => {
  it('should raise error', () => {
    expect(() => buildDateTime('2022-10-11','13')).toThrowError("La date ou l’heure est invalide")
    expect(() => buildDateTime('2022-1011','13:00')).toThrowError("La date ou l’heure est invalide")
  })

  it('should build datetime', () => {
    expect(buildDateTime('2022-10-11','13:00')).toEqual(new Date(2022, 9, 11, 13, 0))
  })

})
