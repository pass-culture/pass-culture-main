import React from 'react'
import { shallow } from 'enzyme'
import { Field, Form } from 'pass-culture-shared'

import RawOffer from '../RawOffer'
import MediationsManager from '../MediationsManager/index'

describe('src | components | pages | Offer | RawOffer ', () => {
  const dispatch = jest.fn()

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        location: {
          search: '?lieu=AQ',
        },
        match: {
          params: {
            offerId: 'N9',
          },
        },
        currentUser: {
          isAdmin: false,
        },
        query: {
          context: () => ({}),
          parse: () => ({ lieu: 'AQ' }),
          translate: () => ({ venue: 'AQ ' }),
        },
        dispatch: dispatch,
        venues: [],
      }

      // when
      const wrapper = shallow(<RawOffer {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('handleSuccess', () => {
    describe('when the offer is successfully modified', () => {
      it('should redirect to offer page', () => {
        // given
        const queryChangeToReadOnly = jest.fn()
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {},
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            changeToReadOnly: queryChangeToReadOnly,
            context: () => ({}),
            parse: () => ({ lieu: 'AQ' }),
            translate: () => ({ venue: 'AQ ' }),
          },
          dispatch: dispatch,
          history: {},
        }

        const wrapper = shallow(<RawOffer {...initialProps} />)

        // when
        const queryParams = { gestion: '' }
        const offer = { id: 'SN' }
        const action = {
          config: { method: 'PATCH' },
          payload: { datum: offer },
        }
        wrapper.instance().handleFormSuccess({}, action)

        // then
        expect(queryChangeToReadOnly).toHaveBeenCalledWith(queryParams, offer)
      })
    })

    describe('when the offer is successfully modified', () => {
      it('should redirect to gestion page', () => {
        // given
        const queryChangeToReadOnly = jest.fn()
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'creation',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            changeToReadOnly: queryChangeToReadOnly,
            context: () => ({}),
            parse: () => ({ lieu: 'AQ' }),
            translate: () => ({ venue: 'AQ ' }),
          },
          dispatch: dispatch,
          history: {},
        }

        const wrapper = shallow(<RawOffer {...initialProps} />)

        // when
        const queryParams = { gestion: '' }
        const offer = { id: 'SN' }
        const action = { config: { method: 'POST' }, payload: { datum: offer } }
        wrapper.instance().handleFormSuccess({}, action)

        // then
        expect(queryChangeToReadOnly).toHaveBeenCalledWith(queryParams, offer)
      })
    })
  })

  describe('render', () => {
    describe('MediationsManager', () => {
      it("should be displayed when it's not a new offer", () => {
        // given
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'N9',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            change: () => {},
            context: () => ({}),
            parse: () => ({ lieu: 'AQ' }),
            translate: () => ({ venue: 'AQ' }),
          },
          dispatch: dispatch,
          offer: {
            bookingEmail: 'fake@email.com',
            dateCreated: '2019-03-29T15:38:23.806900Z',
            dateModifiedAtLastProvider: '2019-03-29T15:38:23.806874Z',
            eventId: null,
            id: 'N9',
            idAtProviders: null,
            isActive: true,
            lastProviderId: null,
            modelName: 'Offer',
            productId: '94',
            venueId: 'AQ',
          },
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)
        const mediationsManagerComponent = wrapper.find(MediationsManager)

        // then
        expect(mediationsManagerComponent).toHaveLength(1)
      })
    })

    describe('when creating a new offer', () => {
      it('should create a new Product when no offer type', () => {
        // given
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'creation',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            change: () => {},
            context: () => ({
              isCreatedEntity: true,
              isModifiedEntity: false,
              readOnly: false,
            }),
            parse: () => ({ lieu: 'AQ' }),
            translate: () => ({ venue: 'AQ' }),
          },
          dispatch: dispatch,
          venues: [],
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)

        // then
        expect(wrapper.find(Form).prop('action')).toEqual('/offers')
      })

      it('should create a new Event when event type given', () => {
        // given
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'creation',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            context: () => ({
              isCreatedEntity: true,
              isModifiedEntity: false,
              readOnly: false,
            }),
            parse: () => ({ lieu: 'AQ' }),
            translate: () => ({ venue: 'AQ' }),
          },
          dispatch: dispatch,
          venues: [],

          selectedOfferType: {
            type: 'Event',
          },
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)

        // then
        expect(wrapper.find(Form).prop('action')).toEqual('/offers')
      })
    })

    describe('when updating the offer', () => {
      it('should update a product when no offer type', () => {
        // given
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'VAG',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            context: () => ({
              isCreatedEntity: false,
              isModifiedEntity: false,
              readOnly: true,
            }),
            parse: () => ({ lieu: 'AQ' }),
            translate: () => ({ venue: 'AQ' }),
          },
          dispatch: dispatch,
          venues: [],
          offer: {
            id: 'VAG',
            productId: 'V24',
          },
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)

        // then
        expect(wrapper.find(Form).prop('action')).toEqual('/offers/VAG')
      })

      it('should create a new Event when event type given', () => {
        // given
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'VAG',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            context: () => ({
              isCreatedEntity: false,
              isModifiedEntity: false,
              readOnly: true,
            }),
            parse: () => ({ lieu: 'AQ' }),
            translate: () => ({ venue: 'AQ' }),
          },
          dispatch: dispatch,
          venues: [],
          selectedOfferType: {
            type: 'Event',
          },
          offer: {
            id: 'VAG',
            eventId: '6GD',
          },
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)

        // then
        expect(wrapper.find(Form).prop('action')).toEqual('/offers/VAG')
      })
    })

    describe('display venue informations', () => {
      const props = {
        location: {
          search: '?lieu=AQ',
        },
        match: {
          params: {
            offerId: 'creation',
          },
        },
        currentUser: {
          isAdmin: false,
        },
        query: {
          change: () => {},
          context: () => ({
            isCreatedEntity: true,
            isModifiedEntity: false,
            readOnly: false,
          }),
          parse: () => ({ lieu: 'AQ' }),
          translate: () => ({ venue: 'AQ' }),
        },
        dispatch: dispatch,
        selectedOfferType: {},
      }

      it('should display venue name when venue publicName is not provided', () => {
        // given
        props.venues = [
          { name: 'quel beau théâtre' },
          { name: 'quel beau musée' },
        ]
        const expectedOptions = [
          { name: 'quel beau théâtre' },
          { name: 'quel beau musée' },
        ]

        // when
        const wrapper = shallow(<RawOffer {...props} />)

        // then
        const fieldGroups = wrapper.find('.field-group')
        const fieldGroupForUsefulInformations = fieldGroups.at(1)
        const venueField = fieldGroupForUsefulInformations.find(Field).at(1)
        expect(fieldGroups).toHaveLength(3)
        expect(venueField.prop('options')).toEqual(expectedOptions)
      })

      it('should display venue public name when venue public name is provided', () => {
        // given
        props.venues = [
          { name: 'quel beau théâtre', publicName: 'quel beau théâtre public' },
          { name: 'quel beau musée', publicName: 'quel beau musée public' },
        ]
        const expectedOptions = [
          {
            name: 'quel beau théâtre public',
            publicName: 'quel beau théâtre public',
          },
          {
            name: 'quel beau musée public',
            publicName: 'quel beau musée public',
          },
        ]

        // when
        const wrapper = shallow(<RawOffer {...props} />)

        // then
        const fieldGroups = wrapper.find('.field-group')
        const fieldGroupForUsefulInformations = fieldGroups.at(1)
        const venueField = fieldGroupForUsefulInformations.find(Field).at(1)
        expect(fieldGroups).toHaveLength(3)
        expect(venueField.prop('options')).toEqual(expectedOptions)
      })
    })
  })
})
