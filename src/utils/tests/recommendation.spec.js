import { setUniqIdOnRecommendation } from '../recommendation'

describe('utils recommendation', () => {
  it('should return an object having an `uniqId` property begining with `product_`', () => {
    // given
    const recommendation = {
      offer: {
        productId: 42,
      },
    }

    // when
    const result = setUniqIdOnRecommendation(recommendation)

    // then
    expect(result.uniqId).toStrictEqual('product_42')
  })

  describe('when recommendation is a tuto', () => {
    it('should return an object having an `uniqId` property begining with `tuto_`', () => {
      // given
      const recommendation = {
        mediation: {
          productId: 42,
          tutoIndex: 'test',
        },
      }

      // when
      const result = setUniqIdOnRecommendation(recommendation)

      // then
      expect(result.uniqId).toStrictEqual('tuto_test')
    })
  })
})
