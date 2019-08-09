import { mapDispatchToProps } from '../DiscoveryContainer'

import { recommendationNormalizer } from '../../../../utils/normalizers'

jest.useFakeTimers()

describe('src | components | pages | discovery | DiscoveryContainer', () => {
  let dispatch
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      history: {},
      location: {
        search: '',
      },
      match: {
        params: {},
      },
      query: {
        parse: () => ({}),
      },
    }
  })

  describe('mapDispatchToProps()', () => {
    it('should load the recommendations with the right configuration', () => {
      // given
      const handleRequestSuccess = jest.fn()
      const handleRequestFail = jest.fn()
      const currentRecommendation = {}
      const recommendations = []
      const readRecommendations = null
      const shouldReloadRecommendations = false

      // when
      mapDispatchToProps(dispatch, props).loadRecommendations(
        handleRequestSuccess,
        handleRequestFail,
        currentRecommendation,
        recommendations,
        readRecommendations,
        shouldReloadRecommendations
      )

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: `/recommendations?`,
          body: {
            readRecommendations: null,
            seenRecommendationIds: [],
          },
          handleFail: handleRequestFail,
          handleSuccess: handleRequestSuccess,
          method: 'PUT',
          normalizer: recommendationNormalizer,
        },
        type: 'REQUEST_DATA_PUT_/RECOMMENDATIONS?',
      })
    })

    it('should call setTimout 2000 times', () => {
      // when
      mapDispatchToProps(dispatch, props).onRequestFailRedirectToHome()

      // then
      expect(setTimeout).toHaveBeenCalledTimes(1)
      expect(setTimeout).toHaveBeenLastCalledWith(expect.any(Function), 2000)
    })

    it('should return undefined when there are no recommendations', () => {
      // given
      const loadedRecommendations = []

      // when
      const redirect = mapDispatchToProps(dispatch, props).redirectToFirstRecommendationIfNeeded(
        loadedRecommendations
      )

      // then
      expect(redirect).toBeUndefined()
    })

    it('should reset recommendations read with the right configuration', () => {
      // when
      mapDispatchToProps(dispatch, props).resetReadRecommendations()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        patch: { readRecommendations: [] },
        type: 'ASSIGN_DATA',
      })
    })

    it('should reset recommendations and bookings with the right configuration', () => {
      // when
      mapDispatchToProps(dispatch, props).resetPageData()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        patch: {
          bookings: [],
          favorites: [],
          mediations: [],
          offers: [],
          recommendations: [],
          stocks: [],
        },
        type: 'ASSIGN_DATA',
      })
    })

    it('should save recommendations loaded timestamp with the right configuration', () => {
      // when
      mapDispatchToProps(dispatch, props).saveLoadRecommendationsTimestamp()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        type: 'SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP',
      })
    })

    it('should return undefined when there is no password', () => {
      // when
      const popin = mapDispatchToProps(dispatch, props).showPasswordChangedPopin()

      // then
      expect(popin).toBeUndefined()
    })
  })
})
