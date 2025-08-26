import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { computeInitialValues } from '../computeInitialValues'

describe('computeInitialValues', () => {
  it('should sort prices', () => {
    expect(
      computeInitialValues(
        getIndividualOfferFactory({
          priceCategories: [
            { id: 1, price: 10, label: 'Cat 1' },
            { id: 2, price: 20, label: 'Cat 2' },
            { id: 3, price: 30, label: 'Cat 3' },
          ],
          isDuo: false,
        })
      )
    ).toEqual({
      isDuo: false,
      priceCategories: [
        { id: 3, label: 'Cat 3', price: 30 },
        { id: 2, label: 'Cat 2', price: 20 },
        { id: 1, label: 'Cat 1', price: 10 },
      ],
    })
  })
})
