import { shallow } from 'enzyme'
import React from 'react'

import BookingsList from '../BookingsList'

describe('src | components | pages | my-bookings | MyBookingsList | BookingsList | BookingsList', () => {
  describe('when I have two bookings', () => {
    it('should render a list of two bookings', () => {
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
      expect(wrapper).toMatchSnapshot()
    })
  })
})
