import { mapDispatchToProps } from '../MyFavoriteDetailsContainer'
import { favoriteNormalizer } from '../../../../../utils/normalizers'

describe('src | components | pages | my-favorite | MyFavoriteDetails | MyFavoriteDetailsContainer', () => {
  describe('requestGetData()', () => {
    it('should dispatch my favorite', () => {
      // given
      const dispatch = jest.fn()
      const ownProps = {
        match: {
          params: {
            favoriteId: 'GA',
          },
        },
      }
      const handleSuccess = jest.fn()

      // when
      mapDispatchToProps(dispatch, ownProps).requestGetData(handleSuccess)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/favorites/GA',
          handleSuccess: expect.any(Function),
          method: 'GET',
          normalizer: favoriteNormalizer,
        },
        type: 'REQUEST_DATA_GET_/FAVORITES/GA',
      })
    })
  })
})
