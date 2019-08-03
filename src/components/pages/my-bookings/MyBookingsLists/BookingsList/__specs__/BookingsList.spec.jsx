import { shallow } from 'enzyme'
import React from 'react'

import BookingsList from '../BookingsList'

describe('src | components | pages | MyBookings | BookingsList', () => {
  it('should match snapshot', () => {
    // given
    const props = {
      bookings: [],
    }

    // when
    const wrapper = shallow(<BookingsList {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
