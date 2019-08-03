import { mapDispatchToProps, mapStateToProps } from '../RecommendationDetailsContainer'

import { recommendationNormalizer } from '../../../../../utils/normalizers'

describe('src | components | pages | search | RecommendationDetailsContainer', () => {
  describe('mapStateToProps', () => {
    it('should return props from state', () => {
      // given
      const mediationId = 'AE'
      const offerId = 'BF'
      const recommendationId = 'CG'
      const recommendation = {
        id: recommendationId,
        mediationId,
        offerId,
      }
      const ownProps = {
        match: {
          params: {
            mediationId,
            offerId,
          },
        },
      }
      const state = {
        data: {
          recommendations: [recommendation],
        },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      const expected = {
        hasReceivedData: true,
        needsToRequestGetData: true,
      }
      expect(result).toStrictEqual(expected)
    })
  })

  describe('mapDispatchToProps', () => {
    it('should dispatch request get recommendation with good config', () => {
      // given
      const dispatch = jest.fn()
      const mediationId = 'AE'
      const offerId = 'BF'
      const ownProps = {
        match: {
          params: {
            mediationId,
            offerId,
          },
        },
      }
      const handleForceDetailsVisible = jest.fn()

      // when
      mapDispatchToProps(dispatch, ownProps).requestGetData(handleForceDetailsVisible)

      // then
      const expected = {
        config: {
          apiPath: `/recommendations/offers/${offerId}?mediationId=${mediationId}`,
          handleSuccess: expect.any(Function),
          method: 'GET',
          normalizer: recommendationNormalizer,
        },
        type: `REQUEST_DATA_GET_/RECOMMENDATIONS/OFFERS/${offerId.toUpperCase()}?MEDIATIONID=${mediationId.toUpperCase()}`,
      }
      expect(dispatch).toHaveBeenCalledWith(expected)
    })
  })
})
