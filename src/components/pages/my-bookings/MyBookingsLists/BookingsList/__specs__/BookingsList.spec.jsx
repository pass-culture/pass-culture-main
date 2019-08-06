import { shallow } from 'enzyme'
import React from 'react'

import BookingsList from '../BookingsList'
import BookingItemContainer from '../BookingItem/BookingItemContainer'

describe('src | components | pages | my-bookings | MyBookingsList | BookingsList | BookingsList', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      bookings: [],
    }

    // when
    const wrapper = shallow(<BookingsList {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('when have two bookings', () => {
    it('should render two bookings', () => {
      // given
      const props = {
        bookings: [
          {
            id: 'ME',
          },
          {
            id: 'FA',
          },
        ],
      }

      // when
      const wrapper = shallow(<BookingsList {...props} />)

      // then
      const bookingItemContainer = wrapper.find(BookingItemContainer)
      expect(bookingItemContainer).toHaveLength(2)
    })
  })
})
