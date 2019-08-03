import {
  mapDispatchToProps,
  onSuccessLoadRecommendationDetails,
} from '../RecommendationItemContainer'

import { recommendationNormalizer } from '../../../../../../utils/normalizers'

describe('src | components | pages | search | Result | RecommendationItemContainer', () => {
  let location
  let props
  let recommendation

  beforeEach(() => {
    recommendation = {
      id: 'QA',
      offer: {
        dateRange: [],
        name: 'sur la route des migrants ; rencontres à Calais',
        product: {
          offerType: {
            appLabel: 'Livres, cartes bibliothèque ou médiathèque',
          },
        },
      },
      offerId: 'X9',
      thumbUrl: 'http://localhost/storage/thumbs/products/QE',
    }
    location = {
      pathname: '/recherche/resultats',
      search: '?categories=Applaudir',
    }
    props = {
      dispatch: jest.fn(),
      history: {
        push: jest.fn(),
      },
      location,
      recommendation,
    }
  })

  describe('onSuccessLoadRecommendationDetails()', () => {
    it('should push URL with vide for null mediation in history', () => {
      // when
      onSuccessLoadRecommendationDetails(props)()

      // then
      const expectedUrl = `${location.pathname}/details/${recommendation.offerId}/vide${location.search}`
      expect(props.history.push).toHaveBeenCalledWith(expectedUrl)
    })

    it('should push URL with mediationId in history', () => {
      // given
      recommendation.mediationId = 'BF'

      // when
      onSuccessLoadRecommendationDetails(props)()

      // then
      const expectedUrl = `${location.pathname}/details/${recommendation.offerId}/${recommendation.mediationId}${location.search}`
      expect(props.history.push).toHaveBeenCalledWith(expectedUrl)
    })
  })

  describe('mapDispatchToProps', () => {
    it('should dispatch the request data', () => {
      // given
      const dispatch = jest.fn()
      const recommendation = {
        id: 'AE',
      }
      const ownProps = {
        recommendation,
      }

      // when
      mapDispatchToProps(dispatch, ownProps).handleMarkSearchRecommendationsAsClicked()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: `/recommendations/${recommendation.id}`,
          body: { isClicked: true },
          handleSuccess: expect.any(Function),
          method: 'PATCH',
          normalizer: recommendationNormalizer,
        },
        type: `REQUEST_DATA_PATCH_/RECOMMENDATIONS/${recommendation.id}`,
      })
    })
  })
})
