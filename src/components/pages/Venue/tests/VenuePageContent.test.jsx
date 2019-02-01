import React from 'react'
import VenuePageContent from '../VenuePageContent'
import { shallow } from 'enzyme'

describe('src | components | pages | Venue | VenuePageContent', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        currentUser: {},
        dispatch: jest.fn(),
        formComment: null,
        formLatitude: 5.15981,
        formLongitude: -52.63452,
        formSiret: '22222222411111',
        history: {},
        location: {
          search: '',
        },
        match: {
          params: {
            offererId: 'APEQ',
            venueId: 'AQYQ',
          },
        },
        name: 'Maison de la Brique',
        offerer: {},
        user: {},
        venuePatch: {},
      }

      // when
      const wrapper = shallow(<VenuePageContent {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('helpers', () => {
    describe('TOTO', () => {
      const venuePatch = {
        address: 'RUE COUACHY',
        bic: null,
        bookingEmail: 'fake@email.com',
        city: 'Kourou',
        comment: null,
        dateModifiedAtLastProvider: '2019-02-01T13:54:57.629916Z',
        departementCode: '97',
        firstThumbDominantColor: null,
        iban: null,
        id: 'AQYQ',
        idAtProviders: null,
        isVirtual: false,
        lastProviderId: null,
        latitude: 5.15981,
        longitude: -52.63452,
        managingOffererId: 'APEQ',
        modelName: 'Venue',
        nOffers: 10,
        name: 'Maison de la Brique',
        postalCode: '97310',
        siret: '22222222411111',
        thumbCount: 0,
        validationToken: null,
      }
    })
  })
  describe('render', () => {
    describe('when editing form', () => {
      it('should permit user to change the e-mail', () => {
        // given
        const props = {
          currentUser: {},
          dispatch: jest.fn(),
          formComment: null,
          formLatitude: 5.15981,
          formLongitude: -52.63452,
          formSiret: '22222222411111',
          history: {},
          location: {
            search: '?modifie',
          },
          match: {
            params: {
              offererId: 'APEQ',
              venueId: 'AQYQ',
            },
          },
          name: 'Maison de la Brique',
          offerer: {},
          user: {},
          venuePatch: {},
        }

        // when
        const wrapper = shallow(<VenuePageContent {...props} />)
        const expected = {
          isEdit: true,
          isLoading: false,
          isNew: false,
          isReadOnly: false,
        }

        // then
        expect(wrapper.state().isReadOnly).toEqual(expected.isReadOnly)
      })
    })
  })
})
