import { offerNormalizer } from '../../../../../utils/normalizers'
import { mapDispatchToProps } from '../MyFavoriteDetailsContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')

  return {
    requestData,
  }
})

describe('src | components MyFavoriteDetailsContainer', () => {
  describe('getOfferById()', () => {
    it('should dispatch my favorite', () => {
      // given
      const dispatch = jest.fn()
      const ownProps = {
        match: {
          params: {
            offerId: 'GA',
          },
        },
      }
      const handleSuccess = jest.fn()

      // when
      mapDispatchToProps(dispatch, ownProps).getOfferById(handleSuccess)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/offers/GA',
          method: 'GET',
          normalizer: offerNormalizer,
        },
        type: 'REQUEST_DATA_GET_/OFFERS/GA',
      })
    })
  })
})
