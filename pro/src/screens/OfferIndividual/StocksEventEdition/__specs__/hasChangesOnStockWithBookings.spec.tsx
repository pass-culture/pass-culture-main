import { stockEventFactory } from 'screens/OfferIndividual/StocksEventEdition/StockFormList/stockEventFactory'

import { hasChangesOnStockWithBookings } from '../StocksEventEdition'

describe('hasChangesOnStockWithBookings', () => {
  it('should return false when no booking quantity', () => {
    const values = { stocks: [] }
    const initialValues = { stocks: [] }

    const result = hasChangesOnStockWithBookings(values, initialValues)
    expect(result).toBe(false)
  })

  it('should return false when booking quantity is 0', () => {
    const values = {
      stocks: [stockEventFactory({ bookingsQuantity: 0 })],
    }
    const initialValues = { stocks: [] }

    const result = hasChangesOnStockWithBookings(values, initialValues)
    expect(result).toBe(false)
  })

  it('should return true when detecting change on price', () => {
    const values = {
      stocks: [
        {
          ...stockEventFactory(),
        },
      ],
    }
    const initialValues = {
      stocks: [
        {
          ...stockEventFactory(),
          price: 42,
        },
      ],
    }

    const result = hasChangesOnStockWithBookings(values, initialValues)
    expect(result).toBe(true)
  })

  it('should return true when detecting change on beginningDate', () => {
    const values = {
      stocks: [
        {
          ...stockEventFactory(),
        },
      ],
    }
    const initialValues = {
      stocks: [
        {
          ...stockEventFactory(),
          beginningDate: new Date(),
        },
      ],
    }

    const result = hasChangesOnStockWithBookings(values, initialValues)
    expect(result).toBe(true)
  })

  it('should return true when detecting change on beginningTime', () => {
    const values = {
      stocks: [
        {
          ...stockEventFactory(),
        },
      ],
    }
    const initialValues = {
      stocks: [
        {
          ...stockEventFactory(),
          beginningTime: new Date(),
        },
      ],
    }
    const result = hasChangesOnStockWithBookings(values, initialValues)
    expect(result).toBe(true)
  })

  it('should return false when detecting change on other field', () => {
    const values = {
      stocks: [
        {
          ...stockEventFactory(),
        },
      ],
    }
    const initialValues = {
      stocks: [
        {
          ...stockEventFactory(),
          bookingQuantity: 42,
        },
      ],
    }
    const result = hasChangesOnStockWithBookings(values, initialValues)
    expect(result).toBe(true)
  })
})
