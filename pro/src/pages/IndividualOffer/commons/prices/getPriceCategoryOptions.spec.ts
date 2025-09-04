import * as convertEuroToPacificFranc from '@/commons/utils/convertEuroToPacificFranc'
import * as formatPrice from '@/commons/utils/formatPrice'

import {
  getPriceCategoryName,
  getPriceCategoryOptions,
} from '../getPriceCategoryOptions'

describe('getPriceCategoryOptions', () => {
  it('should return options sorted by price then label', () => {
    const priceCategories = [
      { id: 1, label: 'Adulte', price: 20 },
      { id: 2, label: 'Enfant', price: 10 },
      { id: 3, label: 'Senior', price: 15 },
    ]
    vi.spyOn(formatPrice, 'formatPrice').mockImplementation(
      (price) => `${price},00 €`
    )
    const options = getPriceCategoryOptions(priceCategories, false)
    expect(options).toEqual([
      { label: '10,00 € - Enfant', value: 2 },
      { label: '15,00 € - Senior', value: 3 },
      { label: '20,00 € - Adulte', value: 1 },
    ])
  })

  it('should return an empty list if priceCategories is undefined', () => {
    expect(getPriceCategoryOptions(undefined, false)).toEqual([])
  })

  it('should return an empty list if priceCategories is null', () => {
    expect(getPriceCategoryOptions(null, false)).toEqual([])
  })
})

describe('getPriceCategoryName', () => {
  it('should format the name in euros', () => {
    vi.spyOn(formatPrice, 'formatPrice').mockImplementation(
      (price) => `${price},00 €`
    )

    expect(
      getPriceCategoryName({ id: 1, label: 'Adulte', price: 20 }, false)
    ).toBe('20,00 € - Adulte')
  })

  it('should format the name in pacific francs', () => {
    vi.spyOn(
      convertEuroToPacificFranc,
      'convertEuroToPacificFranc'
    ).mockImplementation(() => 2392)
    expect(
      getPriceCategoryName({ id: 1, label: 'Adulte', price: 20 }, true)
    ).toBe('2 392 F - Adulte')
  })
})
