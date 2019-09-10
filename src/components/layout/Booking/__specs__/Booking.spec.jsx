import React from 'react'
import { mount, shallow } from 'enzyme'

import BookingCancel from '../BookingCancel/BookingCancel'
import Booking from '../Booking'

describe('src | components | layout |Booking', () => {
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

  describe('cancel view', () => {
    it('should render Booking cancel view when confirmation on match params', () => {
      // given
      props.match.params.confirmation = 'confirmation'

      // when
      const wrapper = shallow(<Booking {...props} />)

      // then
      const bookingCancel = wrapper.find(BookingCancel)
      expect(bookingCancel).toBeDefined()
    })

    describe('when clicking on OK button', () => {
      it('should replace history with url without reservations', () => {
        // given
        props.match.params.confirmation = 'confirmation'
        const wrapper = mount(<Booking {...props} />)
        const okButton = wrapper.find('#booking-cancellation-confirmation-button')

        // when
        okButton.simulate('click')

        // then
        expect(replace.mock.calls[0][0]).toStrictEqual('/foo')
      })
    })

    it('should not add className items-center to the div following the BookingHeader', () => {
      // given
      props.match.params.confirmation = 'confirmation'

      // when
      const wrapper = mount(<Booking {...props} />)

      // then
      const mainWrapper = wrapper.find('.main.flex-rows.flex-1.scroll-y')
      expect(mainWrapper.find('.content.flex-1.flex-center.items-center')).toHaveLength(0)
    })

    it('should not add classNames for padding to the div containing Booking sub-items components', () => {
      // given
      props.match.params.confirmation = 'confirmation'

      // when
      const wrapper = mount(<Booking {...props} />)

      // then
      const mainWrapper = wrapper.find('.main.flex-rows.flex-1.scroll-y')
      expect(mainWrapper.find('.py36.px12.flex-rows')).toHaveLength(0)
    })
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

  it('should let people confirm cancellation', () => {
    // given
    const wrapper = mount(<Booking {...props} />)

    // when
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
    expect(wrapper.find('#booking-cancellation-confirmation-button')).toHaveLength(1)
  })
})
