import { mapStateToProps, mapDispatchToProps } from '../MyFavoritesContainer'

import { favoriteNormalizer } from '../../../../utils/normalizers'

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
        myFavorites: [],
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
      mapDispatchToProps(dispatch).requestGetMyFavorites(handleFail, handleSuccess)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/favorites',
          handleFail: expect.any(Function),
          handleSuccess: expect.any(Function),
          method: 'GET',
          normalizer: favoriteNormalizer,
        },
        type: 'REQUEST_DATA_GET_/FAVORITES',
      })
    })
  })
})
