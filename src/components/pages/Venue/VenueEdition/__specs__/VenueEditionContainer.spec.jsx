import { mapDispatchToProps, mapStateToProps, mergeProps } from '../VenueEditionContainer'
import { venueNormalizer } from '../../../../../utils/normalizers'

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
    it('should return an object with props', () => {
      // given
      const state = {
        data: {
          offerers: [{ id: 1 }],
          userOfferers: [{ offererId: 1, rights: 'admin', userId: 1 }],
          venues: [
            {
              id: 'WQ',
              managingOffererId: 'M4',
            },
          ],
          users: [],
        },
      }
      const props = {
        currentUser: { id: 1 },
        match: {
          params: {
            offererId: 1,
            venueId: 'WQ',
          },
        },
      }

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        offerer: { id: 1 },
        venue: {
          id: 'WQ',
          managingOffererId: 'M4',
        },
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
    query: {
      context: () => ({
        isCreatedEntity: true,
      }),
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
    })
  })

  describe('handleSubmitRequest', () => {
    it('should call patch method with proper params', function () {
      // given
      const ownProps = {
        match: {
          params: {
            venueId: 'TR',
          },
        },
        query: {
          context: () => ({
            method: 'PATCH',
            isCreatedEntity: false,
          }),
        },
      }

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
          apiPath: '/venues/TR',
          body: {
            comment: 'Commentaire',
            address: '3 Place Saint-Michel',
          },
          handleFail: handleFail,
          handleSuccess: handleSuccess,
          method: 'PATCH',
          normalizer: venueNormalizer,
        },
        type: 'REQUEST_DATA_PATCH_/VENUES/TR',
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
        patch: { text: 'Lieu modifié avec succès !', type: 'success' },
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
      trackModifyVenue: expect.any(Function),
    })
  })

  it('should map a tracking event for updating a venue', () => {
    // given
    const stateProps = {}
    const ownProps = {
      tracking: {
        trackEvent: jest.fn(),
      },
    }
    // when
    mergeProps(stateProps, {}, ownProps).trackModifyVenue('RTgfd67')

    // then
    expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
      action: 'modifyVenue',
      name: 'RTgfd67',
    })
  })
})
