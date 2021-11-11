import { shallow } from 'enzyme'
import React from 'react'

import BookingItemContainer from '../BookingItem/BookingItemContainer'
import BookingsList from '../BookingsList'

describe('src | components | BookingsList', () => {
  describe('when I have two bookings', () => {
    it('should display a list of two bookings', () => {
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
      const bookings = wrapper.find(BookingItemContainer)
      expect(bookings).toHaveLength(2)
    })
  })
})
