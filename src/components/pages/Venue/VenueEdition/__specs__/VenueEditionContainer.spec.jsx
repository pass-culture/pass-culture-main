import { mapDispatchToProps, mapStateToProps, mergeProps } from '../VenueEditionContainer'
import { venueNormalizer } from '../../../../../utils/normalizers'
import VenueType from '../../ValueObjects/VenueType'
import VenueLabel from '../../ValueObjects/VenueLabel'

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
        currentUser: { id: 1 },
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
          venues: [
            {
              id: 'WQ',
              managingOffererId: 'M4',
            },
          ],
          users: [],
        },
      }

      // when
      const result = mapStateToProps(state, ownProps)

      // then
      expect(result).toStrictEqual({
        offerer: { id: 1 },
        venue: {
          id: 'WQ',
          managingOffererId: 'M4',
        },
        venueTypes: [],
        venueLabels: [],
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
        data: {
          offerers: [],
          userOfferers: [],
          venues: [],
          'venue-labels': [
            { id: 'AE', label: "CAC - Centre d'art contemporain d'intérêt national" },
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
      const venueLabel = props.venueLabels[0]
      expect(venueLabel).toBeInstanceOf(VenueLabel)
      expect(props).toMatchObject({
        venueLabels: [
          new VenueLabel({ id: 'AE', label: "CAC - Centre d'art contemporain d'intérêt national" }),
          new VenueLabel({ id: 'AF', label: "Ville et Pays d'art et d'histoire" }),
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
    it('should call patch method with proper params', () => {
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
            venueTypeId: null,
            venueLabelId: null,
          },
          handleFail: handleFail,
          handleSuccess: handleSuccess,
          method: 'PATCH',
          normalizer: venueNormalizer,
        },
        type: 'REQUEST_DATA_PATCH_/VENUES/TR',
      })
    })

    describe('when creating a new venue', () => {
      let ownProps
      beforeEach(() => {
        ownProps = {
          match: {
            params: {
              venueId: 'TR',
            },
          },
          query: {
            context: () => ({
              method: 'PATCH',
              isCreatedEntity: true,
            }),
          },
        }
      })

      it('should transform the form values into request payload', () => {
        // given
        const formValues = {
          address: '3 Place Saint-Michel',
          bic: '12345',
          bookingEmail: 'contact@example.net',
          city: 'Paris',
          comment: 'Commentaire',
          iban: 'BHJ2XRT2C',
          latitude: '0.0',
          longitude: '0.0',
          managingOffererId: 'B45S',
          name: 'Théatre Saint-Michel',
          publicName: '',
          postalCode: '75008',
          siret: '25687265176',
          venueTypeId: 'BA',
          venueLabelId: 'DA',
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
        const requestParameters = dispatch.mock.calls[0][0]
        expect(requestParameters.config.body).toStrictEqual({
          address: '3 Place Saint-Michel',
          bookingEmail: 'contact@example.net',
          city: 'Paris',
          comment: 'Commentaire',
          latitude: '0.0',
          longitude: '0.0',
          name: 'Théatre Saint-Michel',
          postalCode: '75008',
          siret: '25687265176',
          venueTypeId: 'BA',
          venueLabelId: 'DA',
        })
      })
    })

    describe('when updating a venue', () => {
      let ownProps
      beforeEach(() => {
        ownProps = {
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
      })

      it('should filter some information that should not be sent', () => {
        // given
        ownProps.query.context = () => ({
          method: 'PATCH',
          isCreatedEntity: false,
        })
        const formValues = {
          address: '3 Place Saint-Michel',
          bic: '12345',
          bookingEmail: 'contact@example.net',
          city: 'Paris',
          comment: 'Commentaire',
          iban: 'BHJ2XRT2C',
          latitude: '0.0',
          longitude: '0.0',
          managingOffererId: 'B45S',
          name: 'Théatre Saint-Michel',
          publicName: '',
          postalCode: '75008',
          siret: '25687265176',
          venueTypeId: 'BA',
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
        const requestParameters = dispatch.mock.calls[0][0]
        expect(requestParameters.config.body).toStrictEqual({
          address: '3 Place Saint-Michel',
          bookingEmail: 'contact@example.net',
          city: 'Paris',
          comment: 'Commentaire',
          latitude: '0.0',
          longitude: '0.0',
          name: 'Théatre Saint-Michel',
          postalCode: '75008',
          siret: '25687265176',
          venueTypeId: 'BA',
          venueLabelId: null,
        })
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
