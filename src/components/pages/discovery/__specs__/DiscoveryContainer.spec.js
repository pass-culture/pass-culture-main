import { mapStateToProps, mapDispatchToProps } from '../DiscoveryContainer'

import { recommendationNormalizer } from '../../../../utils/normalizers'

jest.useFakeTimers()

describe('src | components | pages | discovery | DiscoveryContainer', () => {
  let dispatch
  let replace
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    replace = jest.fn()
    props = {
      history: {
        replace,
      },
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
  describe('mapStateToProps()', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        data: {
          recommendations: [],
        },
      }

      const ownProps = {
        match: {
          params: {},
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toStrictEqual({
        currentRecommendation: {
          index: 0,
          mediation: {
            firstThumbDominantColor: [205, 54, 70],
            frontText:
              'Vous avez parcouru toutes les offres. Revenez bientôt pour découvrir les nouveautés.',
            id: 'fin',
            thumbCount: 1,
            tutoIndex: -1,
          },
          mediationId: 'fin',
          productOrTutoIdentifier: 'tuto_-1',
          thumbUrl: 'http://localhost/splash-finReco@2x.png',
        },
        readRecommendations: undefined,
        recommendations: [],
        shouldReloadRecommendations: true,
        tutos: [],
      })
    })
  })

  describe('mapDispatchToProps()', () => {
    describe('when mapping loadRecommendations', () => {
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
    })

    describe('when mapping onRequestFailRedirectToHome', () => {
      it('should call setTimout 2000 times', () => {
        // when
        mapDispatchToProps(dispatch, props).onRequestFailRedirectToHome()

        // then
        expect(setTimeout).toHaveBeenCalledTimes(1)
        expect(setTimeout).toHaveBeenLastCalledWith(expect.any(Function), 2000)
      })

      it('should replace path by /connexion', () => {
        // given
        jest.useFakeTimers()

        // when
        mapDispatchToProps(dispatch, props).onRequestFailRedirectToHome()
        jest.runAllTimers()

        // then
        expect(replace).toHaveBeenCalledTimes(1)
        expect(replace).toHaveBeenLastCalledWith('/connexion')
      })
    })

    describe('when mapping redirectToFirstRecommendationIfNeeded', () => {
      describe('when there are no recommendations', () => {
        it('should return undefined', () => {
          // given
          const loadedRecommendations = []

          // when
          const redirect = mapDispatchToProps(
            dispatch,
            props
          ).redirectToFirstRecommendationIfNeeded(loadedRecommendations)

          // then
          expect(redirect).toBeUndefined()
        })
      })

      describe('when not on discovery pathname', () => {
        it('should return undefined', () => {
          // given
          const loadedRecommendations = [{ id: 'firstRecommendation' }]
          props.location.pathname = ''

          // when
          const redirect = mapDispatchToProps(
            dispatch,
            props
          ).redirectToFirstRecommendationIfNeeded(loadedRecommendations)

          // then
          expect(redirect).toBeUndefined()
        })
      })

      describe('when visiting for the first time', () => {
        it('should redirect to tuto recommendation with a specified mediation', () => {
          // given
          const dispatch = jest.fn()
          const loadedRecommendations = [{ id: 'QA3D', offerId: null, mediationId: 'A9' }]
          const ownProps = {
            history: {
              replace: jest.fn(),
            },
            match: {
              url: '/decouverte',
              params: {},
            },
          }

          // when
          mapDispatchToProps(dispatch, ownProps).redirectToFirstRecommendationIfNeeded(
            loadedRecommendations
          )

          // then
          expect(ownProps.history.replace).toHaveBeenCalledWith('/decouverte/tuto/A9')
        })

        it('should redirect to tuto recommendation without mediation', () => {
          // given
          const dispatch = jest.fn()
          const loadedRecommendations = [{ id: 'QA3D', offerId: null, mediationId: null }]
          const ownProps = {
            history: {
              replace: jest.fn(),
            },
            match: {
              url: '/decouverte',
              params: {},
            },
          }

          // when
          mapDispatchToProps(dispatch, ownProps).redirectToFirstRecommendationIfNeeded(
            loadedRecommendations
          )

          // then
          expect(ownProps.history.replace).toHaveBeenCalledWith('/decouverte/tuto/vide')
        })

        it('should delete tutos from store when leaving discovery', () => {
          // given
          const tutos = {
            id: 'ABCD',
          }

          // when
          mapDispatchToProps(dispatch, null).deleteTutos(tutos)

          // then
          expect(dispatch).toHaveBeenCalledWith({
            config: {},
            patch: {
              recommendations: {
                id: 'ABCD',
              },
            },
            type: 'DELETE_DATA',
          })
        })
      })
    })

    describe('when mapping resetReadRecommendations', () => {
      it('should reset recommendations with the right configuration', () => {
        // when
        mapDispatchToProps(dispatch, props).resetReadRecommendations()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: { readRecommendations: [] },
          type: 'ASSIGN_DATA',
        })
      })
    })

    describe('when mapping saveLoadRecommendationsTimestamp', () => {
      it('should save recommendations loaded timestamp with the right configuration', () => {
        // when
        mapDispatchToProps(dispatch, props).saveLoadRecommendationsTimestamp()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          type: 'SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP',
        })
      })
    })

    describe('when mapping showPasswordChangedPopin', () => {
      it('should return undefined when there is no password', () => {
        // when
        const popin = mapDispatchToProps(dispatch, props).showPasswordChangedPopin()

        // then
        expect(popin).toBeUndefined()
      })
    })
  })
})
