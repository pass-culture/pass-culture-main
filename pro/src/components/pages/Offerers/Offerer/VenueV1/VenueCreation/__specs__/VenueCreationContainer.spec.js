import { venueNormalizer } from 'utils/normalizers'

import VenueLabel from '../../ValueObjects/VenueLabel'
import VenueType from '../../ValueObjects/VenueType'
import {
  mapDispatchToProps,
  mapStateToProps,
  mergeProps,
} from '../VenueCreationContainer'

jest.mock('../../Notification', () => {
  return jest.fn().mockImplementation(() => 'Some text')
})

window.scroll = () => {}

const mockRequestDataCatch = jest.fn()
jest.mock('redux-saga-data', () => {
  const actualModule = jest.requireActual('redux-saga-data')
  return {
    ...actualModule,
    requestData: config => {
      mockRequestDataCatch(config)
      return actualModule.requestData(config)
    },
  }
})

describe('src | components | pages | VenueContainer | mapStateToProps', () => {
  describe('mapStateToProps', () => {
    let ownProps
    beforeEach(() => {
      ownProps = {
        match: {
          params: {
            offererId: 1,
            venueId: 'WQ',
          },
        },
      }
    })

    it('should return an object with props', () => {
      // given
      const currentUser = { id: 1, email: 'john.doe@email.com' }
      const state = {
        features: {
          list: [],
        },
        data: {
          offerers: [{ id: 1 }],
          userOfferers: [{ offererId: 1, rights: 'admin', userId: 1 }],
          venues: [],
          users: [currentUser],
        },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        currentUser: currentUser,
        isBankInformationWithSiretActive: false,
        isEntrepriseApiDisabled: false,
        offerer: { id: 1 },
        formInitialValues: {
          bookingEmail: 'john.doe@email.com',
          managingOffererId: 1,
        },
        venueTypes: [],
        venueLabels: [],
      })
    })

    it('should map venue types for the component', () => {
      // given
      const state = {
        features: {
          list: [],
        },
        data: {
          offerers: [],
          userOfferers: [],
          venues: [],
          'venue-types': [
            { id: 'AE', label: 'Patrimoine et tourisme' },
            { id: 'AF', label: 'Autre' },
          ],
          users: [
            {
              email: 'john.doe@example.net',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toHaveProperty('venueTypes')
      const venueType = props.venueTypes[0]
      expect(venueType).toBeInstanceOf(VenueType)
      expect(props).toMatchObject({
        venueTypes: [
          new VenueType({ id: 'AE', label: 'Patrimoine et tourisme' }),
          new VenueType({ id: 'AF', label: 'Autre' }),
        ],
      })
    })

    it('should map venue labels for the component', () => {
      // given
      const state = {
        features: {
          list: [],
        },
        data: {
          offerers: [],
          userOfferers: [],
          venues: [],
          'venue-labels': [
            {
              id: 'AE',
              label: "CAC - Centre d'art contemporain d'intérêt national",
            },
            { id: 'AF', label: "Ville et Pays d'art et d'histoire" },
          ],
          users: [
            {
              email: 'john.doe@example.net',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state, ownProps)

      // then
      expect(props).toHaveProperty('venueLabels')
      const venueLabel = props.venueLabels[0]
      expect(venueLabel).toBeInstanceOf(VenueLabel)
      expect(props).toMatchObject({
        venueLabels: [
          new VenueLabel({
            id: 'AE',
            label: "CAC - Centre d'art contemporain d'intérêt national",
          }),
          new VenueLabel({
            id: 'AF',
            label: "Ville et Pays d'art et d'histoire",
          }),
        ],
      })
    })
  })
})

describe('src | components | pages | VenueContainer | mapDispatchToProps', () => {
  let dispatch
  const ownProps = {
    match: {
      params: {
        offererId: 'APEQ',
      },
    },
  }

  beforeEach(() => {
    dispatch = jest.fn()
  })

  describe('handleInitialRequest', () => {
    it('should dispatch action to update existing venue', () => {
      // when
      mapDispatchToProps(dispatch, ownProps).handleInitialRequest(
        jest.fn(),
        jest.fn()
      )

      // then
      expect(dispatch.mock.calls[0][0]).toStrictEqual({
        config: {
          apiPath: '/offerers/APEQ',
          handleSuccess: expect.any(Function),
          method: 'GET',
          normalizer: {
            managedVenues: {
              normalizer: { offers: 'offers' },
              stateKey: 'venues',
            },
          },
        },
        type: 'REQUEST_DATA_GET_/OFFERERS/APEQ',
      })

      expect(dispatch.mock.calls[1][0]).toStrictEqual({
        config: { apiPath: '/userOfferers/APEQ', method: 'GET' },
        type: 'REQUEST_DATA_GET_/USEROFFERERS/APEQ',
      })

      expect(dispatch.mock.calls[2][0]).toStrictEqual({
        config: { apiPath: '/venue-types', method: 'GET' },
        type: 'REQUEST_DATA_GET_/VENUE-TYPES',
      })

      expect(dispatch.mock.calls[3][0]).toStrictEqual({
        config: { apiPath: '/venue-labels', method: 'GET' },
        type: 'REQUEST_DATA_GET_/VENUE-LABELS',
      })
    })
  })

  describe('handleSubmitRequest', () => {
    it('should call patch method with proper params', function () {
      // given
      const formValues = {
        comment: 'Commentaire',
        description: 'description',
        address: '3 Place Saint-Michel',
      }

      const handleFail = jest.fn()
      const handleSuccess = jest.fn()

      // when
      mapDispatchToProps(dispatch, ownProps).handleSubmitRequest({
        formValues,
        handleFail,
        handleSuccess,
      })

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/venues/',
          body: {
            comment: 'Commentaire',
            description: 'description',
            address: '3 Place Saint-Michel',
            venueTypeCode: null,
            venueLabelId: null,
          },
          handleFail: handleFail,
          handleSuccess: handleSuccess,
          method: 'POST',
          normalizer: venueNormalizer,
        },
        type: 'REQUEST_DATA_POST_/VENUES/',
      })
    })
  })

  describe('handleSubmitRequestSuccess', () => {
    it('should dispatch action to display a succes message', () => {
      // given
      const state = {
        features: {
          list: [],
        },
      }
      const action = {
        config: {
          method: 'POST',
        },
        payload: {
          datum: {
            id: 'TR',
          },
        },
      }

      // when
      mapDispatchToProps(dispatch, ownProps).handleSubmitRequestSuccess(
        state,
        action
      )

      // then
      expect(dispatch.mock.calls[0][0]).toStrictEqual({
        payload: { text: 'Some text', type: 'success' },
        type: 'SHOW_NOTIFICATION',
      })
    })
  })
})

describe('src | components | pages | VenueContainer | mergeProps', () => {
  it('should spread stateProps, dispatchProps and ownProps into mergedProps', () => {
    // given
    const stateProps = {}
    const dispatchProps = {
      handleInitialRequest: () => {},
    }
    const ownProps = {
      match: {
        params: {},
      },
    }

    // when
    const mergedProps = mergeProps(stateProps, dispatchProps, ownProps)

    // then
    expect(mergedProps).toStrictEqual({
      match: ownProps.match,
      handleInitialRequest: expect.any(Function),
    })
  })
})
