import { getCurrentRecommendationOfferName } from '../currentRecommendation/getCurrentRecommendationOfferName'
import { selectCurrentRecommendation } from '../currentRecommendation/currentRecommendation'

jest.mock('../currentRecommendation/currentRecommendation')

describe('getCurrentRecommendationOfferName', () => {
  describe('when recommendation does not exist', () => {
    it('should return empty string', () => {
      // given
      selectCurrentRecommendation.mockReturnValue(undefined)
      // then
      expect(getCurrentRecommendationOfferName({})).toBe('')
    })
  })

  describe('when current recommendation does exist', () => {
    describe('when offer not defined', () => {
      it('should return empty string', () => {
        // given
        selectCurrentRecommendation.mockReturnValue({})
        // then
        expect(getCurrentRecommendationOfferName({})).toBe('')
      })
    })

    describe('when offer name not defined', () => {
      it('should return empty string', () => {
        // given
        selectCurrentRecommendation.mockReturnValue({
          offer: {},
        })
        // then
        expect(getCurrentRecommendationOfferName({})).toBe('')
      })
    })

    describe('when offer name is defined', () => {
      it('should return the offername for this recommendation', () => {
        // given
        selectCurrentRecommendation.mockReturnValue({
          offer: {
            name: 'Fake name',
          },
        })
        // then
        expect(getCurrentRecommendationOfferName({})).toBe('Fake name')
      })
    })
  })
})
