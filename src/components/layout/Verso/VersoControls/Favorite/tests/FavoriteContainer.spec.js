import { mapDispatchToProps, mapStateToProps } from '../FavoriteContainer'

import { favoriteNormalizer } from '../../../../../../utils/normalizers'

describe('src | components | layout | Verso | VersoControls | Favorite | FavoriteContainer', () => {
  describe('mapStateToProps', () => {
    it('should return the right props', () => {
      // given
      const mediationId = 'AE'
      const offerId = 'BF'
      const mediation = {
        id: mediationId,
      }
      const offer = {
        id: offerId,
      }
      const favorite = { id: 'CG', offerId }
      const state = {
        data: {
          bookings: [],
          favorites: [favorite],
          features: [],
          mediations: [mediation],
          offers: [offer],
          recommendations: [],
        },
      }
      const ownProps = {
        match: {
          params: {
            mediationId,
            offerId,
          },
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isFavorite: true,
        isFeatureDisabled: true,
        mediationId,
        offerId,
      })
    })
  })

  describe('mapDispatchToProps()', () => {
    it('should add to favorites', () => {
      // given
      const dispatch = jest.fn()
      const mediationId = 'FA'
      const offerId = 'ME'
      const ownProps = {
        history: {},
        location: {
          pathname: '',
        },
      }
      const isFavorite = false
      const showFailModal = jest.fn()

      // when
      mapDispatchToProps(dispatch, ownProps).handleFavorite(
        offerId,
        mediationId,
        isFavorite,
        showFailModal
      )()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/favorites',
          body: {
            mediationId,
            offerId,
          },
          handleFail: showFailModal,
          method: 'POST',
          normalizer: favoriteNormalizer,
        },
        type: 'REQUEST_DATA_POST_/FAVORITES',
      })
    })

    describe('when have offerId and mediationId', () => {
      it('should delete favorite', () => {
        // given
        const dispatch = jest.fn()
        const mediationId = 'FA'
        const offerId = 'ME'
        const ownProps = {
          history: {},
          location: {
            pathname: '',
          },
        }
        const isFavorite = true
        const showFailModal = jest.fn()

        // when
        mapDispatchToProps(dispatch, ownProps).handleFavorite(
          offerId,
          mediationId,
          isFavorite,
          showFailModal
        )()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: `/favorites/${offerId}/${mediationId}`,
            body: {
              mediationId,
              offerId,
            },
            handleFail: showFailModal,
            method: 'DELETE',
            normalizer: favoriteNormalizer,
          },
          type: `REQUEST_DATA_DELETE_/FAVORITES/${offerId.toUpperCase()}/${mediationId.toUpperCase()}`,
        })
      })
    })

    describe('when have offerId only', () => {
      it('should delete favorite', () => {
        // given
        const dispatch = jest.fn()
        const mediationId = null
        const offerId = 'ME'
        const ownProps = {
          history: {},
          location: {
            pathname: '',
          },
        }
        const isFavorite = true
        const showFailModal = jest.fn()

        // when
        mapDispatchToProps(dispatch, ownProps).handleFavorite(
          offerId,
          mediationId,
          isFavorite,
          showFailModal
        )()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: `/favorites/${offerId}`,
            body: {
              mediationId,
              offerId,
            },
            handleFail: showFailModal,
            method: 'DELETE',
            normalizer: favoriteNormalizer,
          },
          type: `REQUEST_DATA_DELETE_/FAVORITES/${offerId.toUpperCase()}`,
        })
      })
    })
  })
})
