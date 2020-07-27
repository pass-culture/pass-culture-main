import { favoriteNormalizer } from '../../../../../utils/normalizers'
import { mapDispatchToProps } from '../../MyFavoritesList/MyFavoritesListContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')

  return {
    requestData,
  }
})

describe('src | components | MyFavorites', () => {
  describe('loadMyFavorites()', () => {
    it('should get my favorites from API', () => {
      // given
      const dispatch = jest.fn()
      const handleFail = jest.fn()
      const handleSuccess = jest.fn()

      // when
      mapDispatchToProps(dispatch).loadMyFavorites(handleFail, handleSuccess)

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

  describe('persistDeleteFavorites()', () => {
    it('should delete my favorites from API', () => {
      // given
      const dispatch = jest.fn()
      const showFailModal = jest.fn()
      const offerIds = ['ME', 'FA']

      // when
      mapDispatchToProps(dispatch).persistDeleteFavorites(showFailModal, offerIds)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: `/favorites/${offerIds[0]}`,
          handleFail: expect.any(Function),
          method: 'DELETE',
        },
        type: 'REQUEST_DATA_DELETE_/FAVORITES/ME',
      })
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: `/favorites/${offerIds[1]}`,
          handleFail: expect.any(Function),
          method: 'DELETE',
        },
        type: 'REQUEST_DATA_DELETE_/FAVORITES/FA',
      })
    })
  })
})
