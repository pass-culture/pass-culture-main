import { CollectiveAdditionalFeeType } from '@/apiClient/v1'

import { computePriceForStock } from '../computePriceForStock'

describe('computePriceForStock', () => {
  it('should return the servicePrice when there are no additional fees', () => {
    expect(computePriceForStock(100, [])).toBe(100)
  })

  it('returns 0 when the service price is 0 and there are no fees', () => {
    expect(computePriceForStock(0, [])).toBe(0)
  })

  it('returns 0 when the service price is null and there are no fees', () => {
    expect(computePriceForStock(null, [])).toBe(0)
  })

  it('adds a single fee to the service price', () => {
    const fees = [
      { amount: 20, label: null, type: CollectiveAdditionalFeeType.TRAVEL },
    ]

    expect(computePriceForStock(100, fees)).toBe(120)
  })

  it('adds multiple fees of different types to the service price', () => {
    const fees = [
      { amount: 10, label: null, type: CollectiveAdditionalFeeType.MEAL },
      {
        amount: 20,
        label: null,
        type: CollectiveAdditionalFeeType.ACCOMMODATION,
      },
      {
        amount: 5,
        label: 'Custom fee',
        type: CollectiveAdditionalFeeType.OTHER,
      },
    ]

    expect(computePriceForStock(100, fees)).toBe(135)
  })

  it('adds multiple fees of different types when service price is null', () => {
    const fees = [
      { amount: 10, label: null, type: CollectiveAdditionalFeeType.MEAL },
      {
        amount: 20,
        label: null,
        type: CollectiveAdditionalFeeType.ACCOMMODATION,
      },
      {
        amount: 5,
        label: 'Custom fee',
        type: CollectiveAdditionalFeeType.OTHER,
      },
    ]

    expect(computePriceForStock(null, fees)).toBe(35)
  })

  it('handles decimal amounts correctly', () => {
    const fees = [
      {
        amount: 1.5,
        label: null,
        type: CollectiveAdditionalFeeType.CONSUMABLE_ITEMS,
      },
      {
        amount: 2.75,
        label: null,
        type: CollectiveAdditionalFeeType.COPYRIGHT,
      },
    ]

    expect(computePriceForStock(10, fees)).toBeCloseTo(14.25)
  })

  it('should return additional fees sum when service price is 0', () => {
    const fees = [
      {
        amount: 15,
        label: null,
        type: CollectiveAdditionalFeeType.APPLICATION_FEE,
      },
      {
        amount: 30,
        label: 'Custom fee',
        type: CollectiveAdditionalFeeType.OTHER,
      },
    ]

    expect(computePriceForStock(0, fees)).toBe(45)
  })
})
