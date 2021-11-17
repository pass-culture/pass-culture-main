import { mapStateToProps, mergeProps } from '../DetailsContainer'

describe('src | components | layout | Details | DetailsContainer', () => {
  let ownProps
  let state

  beforeEach(() => {
    state = {
      data: {
        features: [
          {
            description: `Utiliser la nouvelle web app (d\u00e9cli web/v2) au lieu de l'ancienne`,
            id: 'AHLQ',
            isActive: false,
            name: 'WEBAPP_V2_ENABLED',
            nameKey: 'WEBAPP_V2_ENABLED'
          }
        ]
      },
    }
    ownProps = {
      match: {
        params: {
          booking: 'reservation',
          confirmation: 'confirmation',
        },
      },
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object confirming cancellation', () => {
      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        cancelView: true,
        webAppV2Enabled: false,
      })
    })

    it('should have props.webAppV2Enabled true when WEBAPP_V2_ENABLED is active', () => {
      // when
      const props = mapStateToProps({
        data: {
          features: [
            ...state.data.features.map((feature) => ({
              ...feature,
              isActive: true,
            })),
          ]
        },
      }, ownProps)

      // then
      expect(props).toStrictEqual({
        cancelView: true,
        webAppV2Enabled: true,
      })
    })

    it('should return an object not confirming cancellation', () => {
      // given
      ownProps.match.params.confirmation = undefined

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        cancelView: false,
        webAppV2Enabled: false,
      })
    })
  })

  describe('merge props', () => {
    it('should contain a function to track user who just had been v1 to v2 home redirect', () => {
      // Given
      const ownProps = { tracking: { trackEvent: jest.fn() } }
      const props = mergeProps({}, {}, ownProps)

      // When
      props.trackV1toV2HomeRedirect({ url: 'http://localhost', offerId: '_' })

      // Then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledTimes(1)
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'OfferDetailsContainer_V1toV2HomeRedirect',
        name: 'Redirect: http://localhost - Offer id: _',
      })
    })

    it('should contain a function to track user who just had been v1 to v2 offer redirect', () => {
      // Given
      const ownProps = { tracking: { trackEvent: jest.fn() } }
      const props = mergeProps({}, {}, ownProps)

      // When
      props.trackV1toV2OfferRedirect({ url: 'http://localhost/offre/123', offerId: 'BRXQ' })

      // Then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledTimes(1)
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'OfferDetailsContainer_V1toV2OfferRedirect',
        name: 'Redirect: http://localhost/offre/123 - Offer id: BRXQ',
      })
    })
  })
})
