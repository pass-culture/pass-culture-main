import { shallow } from 'enzyme'
import React from 'react'

import NoBookings from '../NoBookings'

describe('src | components | pages | my-bookings | NoBookings', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<NoBookings />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
