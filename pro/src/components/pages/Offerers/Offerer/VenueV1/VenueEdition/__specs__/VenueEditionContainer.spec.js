/*
 * @debt complexity "Gaël: file over 300 lines"
 * @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
 * @debt complexity "Gaël: file nested too deep in directory structure"
 */

import { venueNormalizer } from 'utils/normalizers'

import VenueLabel from '../../ValueObjects/VenueLabel'
import VenueType from '../../ValueObjects/VenueType'
import { mapDispatchToProps, mapStateToProps } from '../VenueEditionContainer'

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
        features: {
          list: [],
        },
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
        currentUser: undefined,
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
            description: '',
            address: '3 Place Saint-Michel',
            venueTypeCode: null,
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
          contact: {
            email: 'test@test.com',
            phoneNumber: '0606060606',
            website: 'https://test.com',
          },
          comment: 'Commentaire',
          iban: 'BHJ2XRT2C',
          latitude: '0.0',
          longitude: '0.0',
          managingOffererId: 'B45S',
          name: 'Théatre Saint-Michel',
          publicName: '',
          postalCode: '75008',
          siret: '25687265176',
          venueTypeCode: 'BA',
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
          contact: {
            email: 'test@test.com',
            phoneNumber: '0606060606',
            website: 'https://test.com',
          },
          description: '',
          latitude: '0.0',
          longitude: '0.0',
          name: 'Théatre Saint-Michel',
          postalCode: '75008',
          publicName: '',
          siret: '25687265176',
          venueTypeCode: 'BA',
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
          comment: '',
          iban: 'BHJ2XRT2C',
          latitude: '0.0',
          longitude: '0.0',
          managingOffererId: 'B45S',
          name: 'Théatre Saint-Michel',
          publicName: '',
          postalCode: '75008',
          siret: '25687265176',
          venueTypeCode: 'BA',
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
          comment: '',
          description: '',
          latitude: '0.0',
          longitude: '0.0',
          name: 'Théatre Saint-Michel',
          publicName: '',
          postalCode: '75008',
          siret: '25687265176',
          venueTypeCode: 'BA',
          venueLabelId: null,
        })
      })
    })
  })

  describe('handleSubmitRequestSuccess', () => {
    it('should dispatch action to display a succes message', () => {
      // given
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
        action,
        {
          hasDelayedUpdates: false,
        }
      )

      // then
      expect(dispatch.mock.calls[0][0]).toStrictEqual({
        payload: {
          text: 'Vos modifications ont bien été prises en compte',
          type: 'success',
        },
        type: 'SHOW_NOTIFICATION',
      })

      // when
      mapDispatchToProps(dispatch, ownProps).handleSubmitRequestSuccess(
        action,
        {
          hasDelayedUpdates: true,
        }
      )

      // then
      expect(dispatch.mock.calls[1][0]).toStrictEqual({
        payload: {
          text: 'Vos modifications ont bien été prises en compte, cette opération peut durer plusieurs minutes',
          type: 'pending',
        },
        type: 'SHOW_NOTIFICATION',
      })
    })
  })
})
