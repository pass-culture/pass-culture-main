import { OfferIndividual } from 'core/Offers/types'

import { computeInitialValues } from '../computeInitialValues'

describe('computeInitialValues', () => {
  it('should sort prices', () => {
    expect(
      computeInitialValues({
        priceCategories: [
          { price: 10, label: 'Cat 1' },
          { price: 20, label: 'Cat 2' },
          { price: '', label: 'Cat empty' },
          { price: 30, label: 'Cat 3' },
        ],
      } as OfferIndividual)
    ).toEqual({
      isDuo: false,
      priceCategories: [
        { label: 'Cat 3', price: 30 },
        { label: 'Cat 2', price: 20 },
        { label: 'Cat 1', price: 10 },
        { label: 'Cat empty', price: '' },
      ],
    })
  })
})
