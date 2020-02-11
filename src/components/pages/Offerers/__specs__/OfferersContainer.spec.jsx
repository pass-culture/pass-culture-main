import state from '../../../utils/mocks/state'
import { mapStateToProps, mapDispatchToProps, createApiPath } from '../OfferersContainer'

describe('src | components | pages | Offerers | OfferersContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const props = {}

      // when
      const result = mapStateToProps(state, props)

      // then
      const expected = {
        notification: null,
        offerers: [
          {
            address: 'RUE DES SAPOTILLES',
            bic: 'QSDFGH8Z566',
            city: 'Cayenne',
            dateCreated: '2019-03-07T10:39:23.560414Z',
            dateModifiedAtLastProvider: '2019-03-07T10:39:57.823508Z',
            iban: 'FR7630001007941234567890185',
            id: 'BA',
            idAtProviders: null,
            isActive: true,
            isValidated: true,
            lastProviderId: null,
            modelName: 'Offerer',
            nOffers: 5,
            name: 'Bar des amis',
            postalCode: '97300',
            siren: '222222233',
            thumbCount: 0,
            validationToken: null,
          },
          {
            address: 'RUE DES POMMES ROSAS',
            city: 'Cayenne',
            dateCreated: '2019-03-07T10:39:23.560414Z',
            dateModifiedAtLastProvider: '2019-03-07T10:39:57.843884Z',
            id: 'CA',
            idAtProviders: null,
            isActive: true,
            isValidated: false,
            lastProviderId: null,
            modelName: 'Offerer',
            nOffers: 10,
            name: 'Cinéma du coin',
            postalCode: '97300',
            siren: '222222232',
            thumbCount: 0,
            validationToken: 'w3hDQgjYRIyYTxOYY08nwgH3BzI',
          },
        ],
      }
      expect(result).toStrictEqual(expected)
    })
  })

  describe('mapDispatchToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    describe('closeNotification', () => {
      it('enable to close notification', () => {
        // when
        mapDispatchToProps(dispatch).closeNotification()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          type: 'CLOSE_NOTIFICATION',
        })
      })
    })

    describe('loadOfferers', () => {
      it('should load all offerers by default', () => {
        // given
        const ownProps = {
          query: {
            parse: jest.fn().mockReturnValue({}),
          },
        }
        const handleFail = jest.fn()
        const handleSuccess = jest.fn()

        // when
        mapDispatchToProps(dispatch, ownProps).loadOfferers(handleSuccess, handleFail)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offerers',
            handleFail: expect.any(Function),
            handleSuccess: expect.any(Function),
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
          type: 'REQUEST_DATA_GET_/OFFERERS',
        })
      })

      describe('when there is multiple keywords in the url', () => {
        it('should transmit keywords', () => {
          // given
          const ownProps = {
            query: {
              parse: jest.fn().mockReturnValue({
                de: 'Balzac',
                lieu: 'B3',
                'mots-cles': ['Honoré', 'Justice'],
              }),
            },
          }
          const handleFail = jest.fn()
          const handleSuccess = jest.fn()

          // when
          mapDispatchToProps(dispatch, ownProps).loadOfferers(handleSuccess, handleFail)

          // then
          expect(dispatch).toHaveBeenCalledWith({
            config: {
              apiPath: '/offerers?keywords=Honor%C3%A9%20Justice',
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
            type: 'REQUEST_DATA_GET_/OFFERERS?KEYWORDS=HONOR%C3%A9%20JUSTICE',
          })
        })
      })

      describe('when there is one keyword in the url', () => {
        it('should transmit keywords', () => {
          // given
          const ownProps = {
            query: {
              parse: jest.fn().mockReturnValue({
                de: 'Balzac',
                lieu: 'B3',
                'mots-cles': 'Club Dorothy',
              }),
            },
          }
          const handleFail = jest.fn()
          const handleSuccess = jest.fn()

          // when
          mapDispatchToProps(dispatch, ownProps).loadOfferers(handleSuccess, handleFail)

          // then
          expect(dispatch).toHaveBeenCalledWith({
            config: {
              apiPath: '/offerers?keywords=Club%20Dorothy',
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
            type: 'REQUEST_DATA_GET_/OFFERERS?KEYWORDS=CLUB%20DOROTHY',
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
          expect(result).toStrictEqual('/offerers')
        })

        describe('when there is one keyword', () => {
          it('should create api url with keywords params only', () => {
            // given
            const loadOffererParameters = ['example']

            // when
            const result = createApiPath(loadOffererParameters)

            // then
            expect(result).toStrictEqual('/offerers?keywords=example')
          })
        })

        describe('when there is multiple keywords', () => {
          it('should create api url with keywords params only', () => {
            // given
            const loadOffererParameters = ['example', 'keyword']

            // when
            const result = createApiPath(loadOffererParameters)

            // then
            expect(result).toStrictEqual('/offerers?keywords=example%20keyword')
          })
        })
      })
    })

    describe('showNotification', () => {
      it('enable to show notification', () => {
        // given
        const url = '/offerers'

        //when
        mapDispatchToProps(dispatch).showNotification(url)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: {
            tag: 'offerers',
            text:
              'Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)',
            type: 'info',
            url: '/offerers',
            urlLabel: 'Nouveau lieu',
          },
          type: 'SHOW_NOTIFICATION',
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
