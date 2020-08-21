import { selectFavorites } from '../../../../../redux/selectors/data/favoritesSelectors'
import { favoriteNormalizer } from '../../../../../utils/normalizers'
import { mapDispatchToProps, mapStateToProps } from '../../MyFavoritesList/MyFavoritesListContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')

  return {
    requestData,
  }
})
jest.mock('../../../../../redux/selectors/data/favoritesSelectors', () => ({
  selectFavorites: jest.fn(),
}))

describe('src | components | MyFavorites', () => {
  describe('mapStateToProps', () => {
    it('should contain the favorites and the homepage feature', () => {
      // Given
      selectFavorites.mockReturnValue(['mocked favorite'])

      // When
      const props = mapStateToProps(expect.any(Object))

      // Then
      expect(props.myFavorites).toStrictEqual(['mocked favorite'])
    })
  })

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
