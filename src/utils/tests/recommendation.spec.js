import { setUniqIdOnRecommendation } from '../recommendation'

describe('utils recommendation', () => {
  it('should return an object having an `uniqId` property begining with `product_`', () => {
    // Given
    const recommendation = {
      offer: {
        productId: 42,
      },
    }

    // When
    const result = setUniqIdOnRecommendation(recommendation)

    // Then
    expect(result.uniqId).toEqual('product_42')
  })

  describe('when recommendation is a tuto', () => {
    it('should return an object having an `uniqId` property begining with `tuto_`', () => {
      // Given
      const recommendation = {
        mediation: {
          productId: 42,
          tutoIndex: 'test',
        },
      }

      // When
      const result = setUniqIdOnRecommendation(recommendation)

      // Then
      expect(result.uniqId).toEqual('tuto_test')
    })
  })
})
