import '@testing-library/jest-dom'

import { IStockEventFormValues } from 'components/StockEventForm'
import { stockEventFactory } from 'components/StockEventForm/stockEventFactory'

import { hasChangesOnStockWithBookings } from '../StocksEvent'

describe('hasChangesOnStockWithBookings', () => {
  it('should return false when no booking quantity', () => {
    const values = { stocks: [] }
    const initialValues = { stocks: [] }

    const result = hasChangesOnStockWithBookings(values, initialValues)
    expect(result).toBe(false)
  })

  it('should return false when booking quantity is 0', () => {
    const values = {
      stocks: [
        { stockId: 'AA', bookingQuantity: 0 },
      ] as unknown as IStockEventFormValues[],
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
