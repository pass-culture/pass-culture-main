import React from 'react'
import { mount, shallow } from 'enzyme'

import BookingCancel from '../sub-items/BookingCancel'
import Booking from '../Booking'

describe('src | components | booking', () => {
  let props
  let dispatch
  let push

  beforeEach(() => {
    dispatch = jest.fn()
    push = jest.fn()
    props = {
      bookables: [],
      booking: {
        stock: {
          price: 10,
        },
      },
      dispatch,
      history: {
        push,
      },
      isCancelled: false,
      isEvent: false,
      match: {
        params: {
          offerId: 'AAA',
        },
      },
      recommendation: {
        offer: {
          name: 'super offer',
          venue: {
            name: 'super venue',
          },
        },
      },
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Booking {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('cancel view', () => {
    it('should render Booking cancel view when a booking is cancelled', () => {
      // given
      props.isCancelled = true

      // when
      const wrapper = shallow(<Booking {...props} />)

      // then
      const bookingCancel = wrapper.find(BookingCancel)
      expect(bookingCancel).toBeDefined()
    })

    describe('when clicking on OK button', () => {
      it('should dispatch an action to show card view', () => {
        // given
        props.isCancelled = true
        const wrapper = mount(<Booking {...props} />)
        const okButton = wrapper.find('#booking-cancellation-confirmation-button')

        // when
        okButton.simulate('click')

        // then
        expect(dispatch.mock.calls[1][0]).toStrictEqual({ type: 'SHOW_DETAILS_VIEW' })
      })

      it('should dispatch an action to update current user information', () => {
        // given
        props.isCancelled = true
        const wrapper = mount(<Booking {...props} />)
        const okButton = wrapper.find('#booking-cancellation-confirmation-button')

        // when
        okButton.simulate('click')

        // then
        expect(dispatch.mock.calls[0][0]).toStrictEqual({
          config: {
            apiPath: '/users/current',
            method: 'PATCH',
            resolve: expect.any(Function),
          },
          type: 'REQUEST_DATA_PATCH_/USERS/CURRENT',
        })
      })

      it('should redirect to offer details', () => {
        // given
        props.isCancelled = true
        const wrapper = mount(<Booking {...props} />)
        const okButton = wrapper.find('#booking-cancellation-confirmation-button')

        // when
        okButton.simulate('click')

        // then
        expect(push).toHaveBeenCalledWith('/decouverte/AAA')
      })
    })

    it('should not add className items-center to the div following the BookingHeader', () => {
      // given
      props.isCancelled = true

      // when
      const wrapper = mount(<Booking {...props} />)

      // then
      const mainWrapper = wrapper.find('.main.flex-rows.flex-1.scroll-y')
      expect(mainWrapper.find('.content.flex-1.flex-center.items-center')).toHaveLength(0)
    })

    it('should not add classNames for padding to the div containing Booking sub-items components', () => {
      // given
      props.isCancelled = true

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
      props.isCancelled = false

      // when
      const wrapper = mount(<Booking {...props} />)

      // then
      const mainWrapper = wrapper.find('.main')
      expect(mainWrapper.find('.content.flex-1.flex-center.items-center')).toHaveLength(1)
    })

    it('should add classNames for padding to the div containing Booking sub-items components', () => {
      // given
      props.isCancelled = false

      // when
      const wrapper = mount(<Booking {...props} />)

      // then
      const mainWrapper = wrapper.find('.main.flex-rows.flex-1.scroll-y')
      expect(mainWrapper.find('.py36.px12.flex-rows')).toHaveLength(1)
    })
  })
})
