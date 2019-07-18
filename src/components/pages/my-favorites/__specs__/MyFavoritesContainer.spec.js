import { mapStateToProps, mapDispatchToProps } from '../MyFavoritesContainer'

describe('src | components | pages | my-favorites | MyFavorites', () => {
  describe('mapStateToProps()', () => {
    it('should return my favorites', () => {
      // given
      const state = {
        data: {
          favorites: [],
        },
      }

      // when
      const myFavorites = mapStateToProps(state)

      // then
      expect(myFavorites).toStrictEqual({
        myFavorites: []
      })
    })
  })

  describe('mapDispatchToProps()', () => {
    it('should dispatch my favorites', () => {
      // given
      const dispatch = jest.fn()
      const handleFail = jest.fn()
      const handleSuccess = jest.fn()

      // when
      mapDispatchToProps(dispatch).getMyFavorites(handleFail, handleSuccess)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/favorites',
          handleFail: expect.any(Function),
          handleSuccess: expect.any(Function),
          method: 'GET',
          stateKey: 'favorites',
        },
        type: 'REQUEST_DATA_GET_FAVORITES',
      })
    })
  })
})
