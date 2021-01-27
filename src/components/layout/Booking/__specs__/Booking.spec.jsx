import { mount } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'

import Booking from '../Booking'

describe('src | components | layout | Booking | Booking', () => {
  let props

  beforeEach(() => {
    const history = createMemoryHistory()
    history.push({
      pathname: 'offre/details/AAA',
      state: { moduleName: 'Nom du module' },
    })
    props = {
      bookables: [],
      booking: {
        stock: {
          price: 10,
        },
      },
      handleSubmit: jest.fn(),
      history,
      isCancelled: false,
      isEvent: false,
      location: {
        search: '',
      },
      match: {
        params: {
          booking: 'reservations',
          offerId: 'AAA',
          confirmation: 'toto',
        },
        url: '/foo/reservation/AE',
      },
      offer: {
        isEvent: true,
        name: 'super offer',
        venue: {
          name: 'super venue',
        },
        id: 'AAA',
      },
      trackBookingSuccess: jest.fn(),
      trackBookOfferClickFromHomepage: jest.fn(),
      trackBookOfferSuccessFromHomepage: jest.fn(),
      getCurrentUserInformation: jest.fn(),
    }
  })

  describe('when no cancel view', () => {
    it('should add className items-center to the div following the BookingHeader', () => {
      // given
      props.match.params.confirmation = undefined

      // when
      const wrapper = mount(<Booking {...props} />)

      // then
      const mainWrapper = wrapper.find('.main')
      expect(mainWrapper.find('.content.flex-1.flex-center.items-center')).toHaveLength(1)
    })

    it('should add classNames for padding to the div containing Booking sub-items components', () => {
      // given
      props.match.params.confirmation = undefined

      // when
      const wrapper = mount(<Booking {...props} />)

      // then
      const mainWrapper = wrapper.find('.main.flex-rows.flex-1')
      expect(mainWrapper.find('.py36.px12.flex-rows')).toHaveLength(1)
    })
  })

  describe('renderFormControls', () => {
    it('should not display submit button when an error occurs', () => {
      // given
      props.match.params.booking = 'reservation'
      props.match.params.confirmation = undefined

      // when
      const wrapper = mount(<Booking {...props} />)
      const wrapperInstance = wrapper.instance()
      const state = {
        canSubmitForm: true,
        isSubmitting: false,
        bookedPayload: null,
        isErrored: true,
        errors: [],
      }
      wrapperInstance.setState(state)
      wrapper.update()

      // then
      expect(wrapper.find('#booking-close-button')).toHaveLength(1)
      expect(wrapper.find('#booking-validation-button')).toHaveLength(0)
    })
  })

  it('should display submit button when no error occurs', () => {
    // given
    props.match.params.booking = 'reservation'
    props.match.params.confirmation = undefined

    // when
    const wrapper = mount(<Booking {...props} />)
    const wrapperInstance = wrapper.instance()
    const state = {
      canSubmitForm: true,
      isSubmitting: false,
      bookedPayload: null,
      isErrored: false,
    }
    wrapperInstance.setState(state)
    wrapper.update()

    // then
    expect(wrapper.find('#booking-close-button')).toHaveLength(1)
    expect(wrapper.find('#booking-validation-button')).toHaveLength(1)
  })

  describe('analytics', () => {
    it('should not call tracking offer when history location do not contain accueil', () => {
      const mockTrackBookOffer = jest
        .spyOn(props, 'trackBookOfferClickFromHomepage')
        .mockImplementation(jest.fn())
      const mockTrackBookOfferSuccess = jest
        .spyOn(props, 'trackBookOfferSuccessFromHomepage')
        .mockImplementation(jest.fn())

      const wrapper = mount(<Booking {...props} />)
      wrapper.instance().handleFormSubmit({ isDuo: true })

      expect(mockTrackBookOffer).not.toHaveBeenCalled()

      wrapper.instance().handleRequestSuccess({}, { payload: {} })

      expect(mockTrackBookOfferSuccess).not.toHaveBeenCalled()
    })
    it('should call tracking offer when history location contains accueil', () => {
      props.history.push({ pathname: 'accueil/details/AE', state: { moduleName: 'Nom du module' } })
      const mockTrackBookOffer = jest
        .spyOn(props, 'trackBookOfferClickFromHomepage')
        .mockImplementation(jest.fn())
      const mockTrackBookOfferSuccess = jest
        .spyOn(props, 'trackBookOfferSuccessFromHomepage')
        .mockImplementation(jest.fn())

      const wrapper = mount(<Booking {...props} />)

      wrapper.instance().handleFormSubmit({ isDuo: true })

      expect(mockTrackBookOffer).toHaveBeenCalledWith('Nom du module', 'AAA')

      wrapper.instance().handleRequestSuccess({}, { payload: {} })

      expect(mockTrackBookOfferSuccess).toHaveBeenCalledWith('Nom du module', 'AAA')
    })
  })
})
