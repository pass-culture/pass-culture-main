import React from 'react'
import { shallow } from 'enzyme'

import BookingSuccess from '../BookingSuccess'

describe('src | components | layout | Booking | BookingSuccess', () => {
  let props

  beforeEach(() => {
    props = {
      data: {
        token: 'G8G8G8',
        stock: {
          price: 12.5,
        },
      },
      isEvent: true,
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<BookingSuccess {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
