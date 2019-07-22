import { selectCurrentRecommendation } from '../currentRecommendation/currentRecommendation'
import { getCurrentRecommendationOfferName } from '../currentRecommendation/getCurrentRecommendationOffername'

jest.mock('../currentRecommendation/currentRecommendation')

describe('getCurrentRecommendationOfferName', () => {
  describe('when current recommendation does exist', () => {
    describe('when offer not defined', () => {
      it('should return empty string', () => {
        // given
        selectCurrentRecommendation.mockReturnValue({})
        // then
        expect(getCurrentRecommendationOfferName({})).toStrictEqual('')
      })
    })

    describe('when offer name not defined', () => {
      it('should return empty string', () => {
        // given
        selectCurrentRecommendation.mockReturnValue({
          offer: {},
        })
        // then
        expect(getCurrentRecommendationOfferName({})).toStrictEqual('')
      })
    })

    describe('when offer name is defined', () => {
      it('should return the offername for this recommendation', () => {
        // given
        selectCurrentRecommendation.mockReturnValue({
          offer: {
            name: 'offerName',
          },
        })
        // then
        expect(getCurrentRecommendationOfferName({})).toStrictEqual('offerName')
      })
    })
  })
})
