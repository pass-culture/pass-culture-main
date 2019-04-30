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

    it('should redirect to offer details when clicking on OK button', () => {
      // given
      props.isCancelled = true
      const wrapper = mount(<Booking {...props} />)
      const okButton = wrapper.find('#booking-cancel-ok-button')

      // when
      okButton.simulate('click')

      // then
      expect(dispatch).toHaveBeenCalledWith({ type: 'SHOW_DETAILS_VIEW' })
      expect(push).toHaveBeenCalledWith('/decouverte/AAA')
    })
  })
})
