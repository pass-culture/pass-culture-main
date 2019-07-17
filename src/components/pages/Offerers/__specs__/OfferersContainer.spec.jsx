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
        pendingOfferers: [],
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
          pendingOfferers: [],
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

    it('enable to load offerers', () => {
      // when
      const apiPath = '/offerers'
      const handleFail = jest.fn()
      const handleSuccess = jest.fn()
      mapDispatchToProps(dispatch).loadOfferers(apiPath, handleFail, handleSuccess)

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

    it('enable to load not validated offerers', () => {
      // when
      const apiPath = '/offerers'
      mapDispatchToProps(dispatch).loadNotValidatedUserOfferers(apiPath)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/offerers',
          method: 'GET',
          normalizer: {
            managedVenues: {
              normalizer: {
                offers: 'offers',
              },
              stateKey: 'venues',
            },
          },
          stateKey: 'pendingOfferers',
        },
        type: 'REQUEST_DATA_GET_PENDINGOFFERERS',
      })
    })

    it('enable to show notification', () => {
      //when
      const url = '/offerers'
      mapDispatchToProps(dispatch).showNotification(url)

      // then
      expect(dispatch).toHaveBeenCalledWith(
        {
          "patch": {
            "tag": "offerers",
            "text": "Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)",
            "type": "info",
            "url": "/offerers",
            "urlLabel": "Nouveau lieu",
          },
          "type": "SHOW_NOTIFICATION",
        }
      )
    })
  })
})
