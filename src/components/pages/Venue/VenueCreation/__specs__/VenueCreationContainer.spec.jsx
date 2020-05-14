import { mapDispatchToProps, mapStateToProps, mergeProps } from '../VenueCreationContainer'
import { venueNormalizer } from '../../../../../utils/normalizers'
import VenueType from '../../ValueObjects/VenueType'

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
        currentUser: { id: 1, email: 'john.doe@email.com' },
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
      const state = {
        data: {
          offerers: [{ id: 1 }],
          userOfferers: [{ offererId: 1, rights: 'admin', userId: 1 }],
          venues: [],
          users: [],
        },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        offerer: { id: 1 },
        formInitialValues: {
          bookingEmail: 'john.doe@email.com',
          managingOffererId: 1,
        },
        venueTypes: [],
      })
    })

    it('should map venue types for the component', () => {
      // given
      const state = {
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
      mapDispatchToProps(dispatch, ownProps).handleInitialRequest(jest.fn(), jest.fn())

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
    })
  })

  describe('handleSubmitRequest', () => {
    it('should call patch method with proper params', function() {
      // given
      const formValues = {
        comment: 'Commentaire',
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
            address: '3 Place Saint-Michel',
            venueTypeId: null,
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
      const state = {}
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
      mapDispatchToProps(dispatch, ownProps).handleSubmitRequestSuccess(state, action)

      // then
      expect(dispatch.mock.calls[0][0]).toStrictEqual({
        patch: { text: 'Some text', type: 'success' },
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
      trackCreateVenue: expect.any(Function),
    })
  })

  it('should map a tracking event for creating a venue', () => {
    // given
    const stateProps = {}
    const ownProps = {
      tracking: {
        trackEvent: jest.fn(),
      },
    }

    // when
    mergeProps(stateProps, {}, ownProps).trackCreateVenue('RTgfd67')

    // then
    expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
      action: 'createVenue',
      name: 'RTgfd67',
    })
  })
})
