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
        const handleFail = jest.fn()
        const handleSuccess = jest.fn()

        // when
        mapDispatchToProps(dispatch).loadOfferers(handleSuccess, handleFail)

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

      it('can load only validated offerers', () => {
        // given
        const handleFail = jest.fn()
        const handleSuccess = jest.fn()

        // when
        mapDispatchToProps(dispatch).loadOfferers(handleSuccess, handleFail, { isValidated: true })

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offerers?validated=true',
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
          type: 'REQUEST_DATA_GET_/OFFERERS?VALIDATED=TRUE',
        })
      })

      it('can load offerers by keywords', () => {
        // given
        const handleFail = jest.fn()
        const handleSuccess = jest.fn()

        // when
        mapDispatchToProps(dispatch).loadOfferers(handleSuccess, handleFail, {
          isValidated: true,
          keywords: 'keywords=nice%20words',
        })

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offerers?validated=true&keywords=nice%20words',
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
          type: 'REQUEST_DATA_GET_/OFFERERS?VALIDATED=TRUE&KEYWORDS=NICE%20WORDS',
        })
      })

      it('can load only offerers that are not validated yet', () => {
        // given
        const handleFail = jest.fn()
        const handleSuccess = jest.fn()

        // when
        mapDispatchToProps(dispatch).loadOfferers(handleSuccess, handleFail, { isValidated: false })

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offerers?validated=false',
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
          type: 'REQUEST_DATA_GET_/OFFERERS?VALIDATED=FALSE',
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

  describe('createApiPath', () => {
    it('should create api url with no params', () => {
      // given
      const loadOffererParameters = {}
      // when
      const result = createApiPath(loadOffererParameters)

      // then
      expect(result).toStrictEqual('/offerers')
    })

    it('should create api url with keywords params only', () => {
      // given
      const loadOffererParameters = {
        keywords: 'keywords=example',
      }

      // when
      const result = createApiPath(loadOffererParameters)

      // then
      expect(result).toStrictEqual('/offerers?keywords=example')
    })

    it('should create api url with isValidated params only', () => {
      // given
      const loadOffererParameters = {
        isValidated: true,
      }

      // when
      const result = createApiPath(loadOffererParameters)

      // then
      expect(result).toStrictEqual('/offerers?validated=true')
    })

    it('should create api url with keywords and isValidated params even if is value is false', () => {
      // given
      const loadOffererParameters = {
        isValidated: false,
        keywords: 'keywords=example',
      }

      // when
      const result = createApiPath(loadOffererParameters)

      // then
      expect(result).toStrictEqual('/offerers?validated=false&keywords=example')
    })
  })
})
