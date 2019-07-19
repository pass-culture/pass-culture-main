import currentRecommendationSelector from '../../../../../selectors/currentRecommendation/currentRecommendation'
import { mergeDataWithStore, mapStateToProps, mapDispatchToProps } from '../FavoriteContainer'

jest.mock('../../../../../selectors/currentRecommendation/currentRecommendation')

describe('src | components | verso | verso-controls | favorite | FavoriteContainer', () => {
  describe('mergeDataWithStore()', () => {
    it('should merge data with the store when the offer is already in favorites', () => {
      // given
      const dispatch = jest.fn()
      const isFavorite = true
      const recommendation = {}
      const state = {}
      const action = {}

      // when
      mergeDataWithStore(dispatch, isFavorite, recommendation)(state, action)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {},
        patch: {
          recommendations: [
            {
              offer: {
                favorites: [],
              },
            },
          ],
        },
        type: 'MERGE_DATA',
      })
    })

    it('should merge data with the store when the offer is not in favorites', () => {
      // given
      const dispatch = jest.fn()
      const isFavorite = false
      const recommendation = {}
      const state = {}
      const action = {
        payload: {
          datum: 'toto',
        },
      }

      // when
      mergeDataWithStore(dispatch, isFavorite, recommendation)(state, action)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {},
        patch: {
          recommendations: [
            {
              offer: {
                favorites: ['toto'],
              },
            },
          ],
        },
        type: 'MERGE_DATA',
      })
    })
  })

  describe('mapStateToProps()', () => {
    it('should return the right props', () => {
      // given
      const ownProps = {
        match: {
          params: {
            mediationId: 'AHJQ',
            offerId: 'A93Q',
          },
        },
      }
      const state = {}
      currentRecommendationSelector.mockReturnValue({
        offer: {
          favorites: [],
        },
      })

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        recommendation: {
          offer: {
            favorites: [],
          },
        },
      })
    })
  })

  describe('mapDispatchToProps()', () => {
    it('should add to favorites', () => {
      // given
      const dispatch = jest.fn()
      const isFavorite = false
      const recommendation = {
        mediationId: 'FA',
        offerId: 'ME',
      }
      const showFailModal = jest.fn()

      // when
      mapDispatchToProps(dispatch).handleFavorite(isFavorite, recommendation, showFailModal)()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/offers/favorites',
          body: {
            mediationId: recommendation.mediationId,
            offerId: recommendation.offerId,
          },
          handleFail: showFailModal,
          handleSuccess: expect.any(Function),
          method: 'POST',
          stateKey: 'offersFavorites',
        },
        type: 'REQUEST_DATA_POST_OFFERSFAVORITES',
      })
    })

    it('should delete favorite', () => {
      // given
      const dispatch = jest.fn()
      const isFavorite = true
      const recommendation = {
        mediationId: 'FA',
        offerId: 'ME',
      }
      const showFailModal = jest.fn()

      // when
      mapDispatchToProps(dispatch).handleFavorite(isFavorite, recommendation, showFailModal)()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: `/offers/favorites/${recommendation.offerId}/${recommendation.mediationId}`,
          body: {
            mediationId: recommendation.mediationId,
            offerId: recommendation.offerId,
          },
          handleFail: showFailModal,
          handleSuccess: expect.any(Function),
          method: 'DELETE',
          stateKey: 'offersFavorites',
        },
        type: 'REQUEST_DATA_DELETE_OFFERSFAVORITES',
      })
    })
  })
})
