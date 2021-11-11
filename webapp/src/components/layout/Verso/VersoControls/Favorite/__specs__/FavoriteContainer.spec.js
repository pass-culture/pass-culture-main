import { mapDispatchToProps, mapStateToProps } from '../FavoriteContainer'

jest.mock('../../../../../../utils/fetch-normalize-data/requestData', () => {
  const { _requestData } = jest.requireActual(
    '../../../../../../utils/fetch-normalize-data/reducers/data/actionCreators'
  )

  return {
    requestData: _requestData,
  }
})

describe('components | FavoriteContainer', () => {
  describe('mapStateToProps', () => {
    let state
    let ownProps

    beforeEach(() => {
      state = {
        data: {
          bookings: [],
          favorites: [],
          features: [],
          mediations: [],
          offers: [],
        },
      }
      ownProps = {
        match: {
          params: {},
        },
      }
    })

    it('should return the right props when mediationId is available', () => {
      // given
      const offerId = 'BF'
      const mediationId = 'AE'
      state.data.favorites = [{ id: 'CG', offerId }]
      state.data.mediations = [{ id: mediationId, offerId }]
      ownProps.match.params.offerId = offerId

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isFavorite: true,
        mediationId,
        offerId,
      })
    })

    it('should return the right props when bookingId is available', () => {
      // given
      const bookingId = 'AC'
      const mediationId = 'AE'
      const offerId = 'BF'
      state.data.bookings = [{ id: bookingId, stockId: 'AG' }]
      state.data.favorites = [{ id: 'CG', offerId }]
      state.data.mediations = [{ id: mediationId, offerId }]
      state.data.offers = [{ id: offerId }]
      state.data.stocks = [{ id: 'AG', offerId }]
      ownProps.match.params.bookingId = bookingId

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        isFavorite: true,
        mediationId,
        offerId,
      })
    })

    describe('isFavorite', () => {
      it('should be false when no offer marked as favorite', () => {
        // given
        const state = {
          data: {
            bookings: [],
            favorites: [],
            features: [],
            mediations: [
              {
                id: 'AE',
              },
            ],
            offers: [
              {
                id: 'BF',
              },
            ],
          },
        }
        const ownProps = {
          match: {
            params: {
              mediationId: 'AE',
              offerId: 'BF',
            },
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toHaveProperty('isFavorite', false)
      })

      it('should be true when offer is marked as favorite', () => {
        // given
        const state = {
          data: {
            bookings: [],
            favorites: [
              {
                offerId: 'BF',
              },
            ],
            features: [],
            mediations: [
              {
                id: 'AE',
              },
            ],
            offers: [
              {
                id: 'BF',
              },
            ],
          },
        }
        const ownProps = {
          match: {
            params: {
              mediationId: 'AE',
              offerId: 'BF',
            },
          },
        }

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toHaveProperty('isFavorite', true)
      })
    })
  })

  describe('mapDispatchToProps()', () => {
    describe('handleFavorite()', () => {
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
          },
          type: 'REQUEST_DATA_POST_/FAVORITES',
        })
      })

      describe('when have offerId', () => {
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
              apiPath: `/favorites/${offerId}`,
              body: {
                mediationId,
                offerId,
              },
              handleFail: showFailModal,
              method: 'DELETE',
            },
            type: `REQUEST_DATA_DELETE_/FAVORITES/${offerId.toUpperCase()}`,
          })
        })
      })
    })

    describe('loadFavorites()', () => {
      it('should load all favorites', () => {
        // given
        const dispatch = jest.fn()

        // when
        mapDispatchToProps(dispatch).loadFavorites()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/favorites',
            method: 'GET',
          },
          type: 'REQUEST_DATA_GET_/FAVORITES',
        })
      })
    })
  })
})
