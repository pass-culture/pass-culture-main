import { mapStateToProps, mapDispatchToProps } from '../MyFavoriteDetailsContainer'

import { favoriteNormalizer } from '../../../../../utils/normalizers'

describe('src | components | pages | my-favorite | MyFavoriteDetails | MyFavoriteDetailsContainer', () => {
  describe('mapStateToProps()', () => {
    it('should return an object', () => {
      // given
      const state = {
        data: {
          favorites: [
            {
              id: 'GA',
            },
          ],
        },
      }
      const ownProps = {
        match: {
          params: {
            favoriteId: 'GA',
          },
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        needsToRequestGetData: false,
      })
    })
  })

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
