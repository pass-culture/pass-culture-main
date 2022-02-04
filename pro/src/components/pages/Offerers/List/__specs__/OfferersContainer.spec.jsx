import state from 'components/utils/mocks/state'

import {
  mapStateToProps,
  mapDispatchToProps,
  createApiPath,
} from '../OfferersContainer'

describe('src | components | pages | Offerers | OfferersContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const props = {}

      // when
      const result = mapStateToProps(state, props)

      // then
      const expected = {
        isOffererCreationAvailable: false,
        offerers: [
          {
            address: 'RUE DES SAPOTILLES',
            bic: 'QSDFGH8Z566',
            city: 'Cayenne',
            dateCreated: '2019-03-07T10:39:23.560414Z',
            dateModifiedAtLastProvider: '2019-03-07T10:39:57.823508Z',
            iban: 'FR7630001007941234567890185',
            id: 'BA',
            isActive: true,
            isValidated: true,
            lastProviderId: null,
            modelName: 'Offerer',
            nOffers: 5,
            name: 'Bar des amis',
            postalCode: '97300',
            siren: '222222233',
            validationToken: null,
          },
          {
            address: 'RUE DES POMMES ROSAS',
            city: 'Cayenne',
            dateCreated: '2019-03-07T10:39:23.560414Z',
            dateModifiedAtLastProvider: '2019-03-07T10:39:57.843884Z',
            id: 'CA',
            isActive: true,
            isValidated: false,
            lastProviderId: null,
            modelName: 'Offerer',
            nOffers: 10,
            name: 'Cinéma du coin',
            postalCode: '97300',
            siren: '222222232',
            validationToken: 'w3hDQgjYRIyYTxOYY08nwgH3BzI',
          },
        ],
      }
      expect(result).toStrictEqual(expected)
    })

    describe('isOffererCreationAvailable is based on feature flipping', () => {
      it('should mark offerer creation possible when API sirene is available', () => {
        // given
        const props = {}
        const state = {
          data: {},
          features: {
            list: [
              {
                isActive: true,
                nameKey: 'API_SIRENE_AVAILABLE',
              },
            ],
          },
        }

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('isOffererCreationAvailable', true)
      })

      it('should prevent offerer creation when feature API sirene is not available', () => {
        // given
        const props = {}
        const state = {
          data: {},
          features: {
            list: [
              {
                isActive: false,
                nameKey: 'API_SIRENE_AVAILABLE',
              },
            ],
          },
        }

        // when
        const result = mapStateToProps(state, props)

        // then
        expect(result).toHaveProperty('isOffererCreationAvailable', false)
      })
    })
  })

  describe('mapDispatchToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    describe('loadOfferers', () => {
      let handleFail
      let handleSuccess
      let ownProps

      beforeEach(() => {
        handleFail = jest.fn()
        handleSuccess = jest.fn()

        ownProps = {
          query: {
            parse: jest.fn().mockReturnValue({}),
          },
        }
      })

      it('should request for all offerers by default', () => {
        // when
        mapDispatchToProps(dispatch, ownProps).loadOfferers(
          handleSuccess,
          handleFail
        )

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offerers?page=0',
            handleFail,
            handleSuccess,
            method: 'GET',
            normalizer: {
              managedVenues: {
                normalizer: {
                  offers: 'offers',
                },
                stateKey: 'venues',
              },
            },
          },
          type: 'REQUEST_DATA_GET_/OFFERERS?PAGE=0',
        })
      })

      describe('when there is multiple keywords in the url', () => {
        it('should transmit keywords', () => {
          // given
          ownProps.query.parse.mockReturnValue({
            de: 'Balzac',
            lieu: 'B3',
            'mots-cles': ['Honoré', 'Justice'],
          })

          // when
          mapDispatchToProps(dispatch, ownProps).loadOfferers(
            handleSuccess,
            handleFail
          )

          // then
          expect(dispatch).toHaveBeenCalledWith({
            config: {
              apiPath: '/offerers?keywords=Honor%C3%A9+Justice&page=0',
              handleFail,
              handleSuccess,
              method: 'GET',
              normalizer: {
                managedVenues: {
                  normalizer: {
                    offers: 'offers',
                  },
                  stateKey: 'venues',
                },
              },
            },
            type: 'REQUEST_DATA_GET_/OFFERERS?KEYWORDS=HONOR%C3%A9+JUSTICE&PAGE=0',
          })
        })
      })

      describe('when there is one keyword in the url', () => {
        it('should transmit keyword', () => {
          // given
          ownProps.query.parse.mockReturnValue({
            de: 'Balzac',
            lieu: 'B3',
            'mots-cles': 'Club Dorothy',
          })

          // when
          mapDispatchToProps(dispatch, ownProps).loadOfferers(
            handleSuccess,
            handleFail
          )

          // then
          expect(dispatch).toHaveBeenCalledWith({
            config: {
              apiPath: '/offerers?keywords=Club+Dorothy&page=0',
              handleFail,
              handleSuccess,
              method: 'GET',
              normalizer: {
                managedVenues: {
                  normalizer: {
                    offers: 'offers',
                  },
                  stateKey: 'venues',
                },
              },
            },
            type: 'REQUEST_DATA_GET_/OFFERERS?KEYWORDS=CLUB+DOROTHY&PAGE=0',
          })
        })
      })

      describe('createApiPath', () => {
        it('should create api url with no params', () => {
          // given
          const loadOffererKeyWords = []
          // when
          const result = createApiPath(loadOffererKeyWords)

          // then
          expect(result).toBe('/offerers')
        })

        describe('when there is one keyword', () => {
          it('should create api url with keywords params only', () => {
            // given
            const loadOffererParameters = ['example']

            // when
            const result = createApiPath(loadOffererParameters)

            // then
            expect(result).toBe('/offerers?keywords=example')
          })
        })

        describe('when there is multiple keywords', () => {
          it('should create api url with keywords params only', () => {
            // given
            const loadOffererParameters = ['example', 'keyword']

            // when
            const result = createApiPath(loadOffererParameters)

            // then
            expect(result).toBe('/offerers?keywords=example+keyword')
          })
        })
      })
    })

    describe('resetLoadedOfferers', () => {
      it('should clean the offerers already loaded with an ASSIGN_DATA event', () => {
        // given
        const functions = mapDispatchToProps(dispatch)

        // then
        functions.resetLoadedOfferers()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: {
            offerers: [],
          },
          type: 'ASSIGN_DATA',
        })
      })
    })
  })
})
