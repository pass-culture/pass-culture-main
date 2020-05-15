import React from 'react'
import { shallow } from 'enzyme'

import BookingSuccess from '../BookingSuccess'

describe('src | components | layout | Booking | BookingSuccess', () => {
  let props

  beforeEach(() => {
    props = {
      isEvent: true,
      offerUrl: 'http://fake-url.com',
      price: 12.5,
      quantity: 1,
      token: 'G8G8G8',
    }
  })

  it('should match the snapshot when booking an event', () => {
    // when
    const wrapper = shallow(<BookingSuccess {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should match the snapshot when booking a duo event', () => {
    // given
    props.quantity = 2

    // when
    const wrapper = shallow(<BookingSuccess {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should match the snapshot when booking a thing event', () => {
    // givn
    props.quantity = 1
    props.isEvent = false

    // when
    const wrapper = shallow(<BookingSuccess {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
