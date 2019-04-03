import React from 'react'
import { shallow } from 'enzyme'

import RawOffer from '../RawOffer'
import MediationsManager from '../MediationsManager/index'
import { Form } from 'pass-culture-shared'

const dispatchMock = jest.fn()

describe('src | components | pages | Offer | RawOffer ', () => {
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
          parse: () => ({ lieu: 'AQ' }),
        },
        dispatch: dispatchMock,
        venues: [],
      }

      // when
      const wrapper = shallow(<RawOffer {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
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
            parse: () => ({ lieu: 'AQ' }),
          },
          dispatch: dispatchMock,
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
            thingId: '94',
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
      it('should create a new Thing when no offer type', () => {
        // given
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'nouveau',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            parse: () => ({ lieu: 'AQ' }),
          },
          dispatch: dispatchMock,
          venues: [],
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)

        // then
        expect(wrapper.find(Form).prop('action')).toEqual('offers/')
      })

      it('should create a new Event when event type given', () => {
        // given
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'nouveau',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            parse: () => ({ lieu: 'AQ' }),
          },
          dispatch: dispatchMock,
          venues: [],

          selectedOfferType: {
            type: 'Event',
          },
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)

        // then
        expect(wrapper.find(Form).prop('action')).toEqual('offers/')
      })
    })

    describe('when updating the offer', () => {
      it('should update a thing when no offer type', () => {
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
            parse: () => ({ lieu: 'AQ' }),
          },
          dispatch: dispatchMock,
          venues: [],
          offer: {
            thingId: 'V24',
          },
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)

        // then
        expect(wrapper.find(Form).prop('action')).toEqual('offers/VAG')
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
            parse: () => ({ lieu: 'AQ' }),
          },
          dispatch: dispatchMock,
          venues: [],
          selectedOfferType: {
            type: 'Event',
          },
          offer: {
            eventId: '6GD',
          },
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)

        // then
        expect(wrapper.find(Form).prop('action')).toEqual('offers/VAG')
      })
    })
  })
})
