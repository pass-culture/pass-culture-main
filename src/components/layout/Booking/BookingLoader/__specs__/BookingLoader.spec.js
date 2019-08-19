import React from 'react'
import { shallow } from 'enzyme'

import BookingLoader from '../BookingLoader'

describe('src | components | layout | Booking | BookingLoader', () => {
  let props

  beforeEach(() => {
    props = {
      errors: {},
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<BookingLoader {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
