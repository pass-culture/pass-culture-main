import state from '../../../utils/mocks/state'
import { mapStateToProps, mapDispatchToProps } from '../OfferersContainer'

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
            firstThumbDominantColor: null,
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
            firstThumbDominantColor: null,
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

    it('enable to assign data', () => {
      // when
      mapDispatchToProps(dispatch).assignData()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        patch: {
          offerers: [],
        },
        type: 'ASSIGN_DATA',
      })
    })

    it('enable to close notification', () => {
      // when
      mapDispatchToProps(dispatch).closeNotification()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        type: 'CLOSE_NOTIFICATION',
      })
    })

    describe('loadOfferers', () => {
      it('load all offerers by default', () => {
        // when
        const handleFail = jest.fn()
        const handleSuccess = jest.fn()
        mapDispatchToProps(dispatch).loadOfferers(handleFail, handleSuccess)

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
        // when
        const handleFail = jest.fn()
        const handleSuccess = jest.fn()
        mapDispatchToProps(dispatch).loadOfferers(handleFail, handleSuccess, { isValidated: true })

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

      it('can load only offerers that are not validated yet', () => {
        // when
        const handleFail = jest.fn()
        const handleSuccess = jest.fn()
        mapDispatchToProps(dispatch).loadOfferers(handleFail, handleSuccess, { isValidated: false })

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

    it('enable to show notification', () => {
      //when
      const url = '/offerers'
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
})
