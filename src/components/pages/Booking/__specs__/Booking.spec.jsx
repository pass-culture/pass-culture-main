import React from 'react'
import { mount, shallow } from 'enzyme'

import Booking from '../Booking'

describe('src | components | layout | Booking | Booking', () => {
  let props
  let push
  let replace
  let handleSubmit
  let trackBookingSuccess

  beforeEach(() => {
    push = jest.fn()
    replace = jest.fn()
    handleSubmit = jest.fn()
    trackBookingSuccess = jest.fn()
    props = {
      bookables: [],
      booking: {
        stock: {
          price: 10,
        },
      },
      handleSubmit,
      history: {
        push,
        replace,
      },
      isCancelled: false,
      isEvent: false,
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
      },
      recommendation: {
        id: 'AE',
      },
      trackBookingSuccess,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Booking {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
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
      const mainWrapper = wrapper.find('.main.flex-rows.flex-1.scroll-y')
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
})
