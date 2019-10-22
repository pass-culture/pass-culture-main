import React from 'react'
import { shallow } from 'enzyme'

import BookingSuccess from '../BookingSuccess'

describe('src | components | layout | Booking | BookingSuccess', () => {
  let props

  beforeEach(() => {
    props = {
      bookedPayload: {
        completedUrl: 'http://fake-url.com',
        quantity: 1,
        token: 'G8G8G8',
        stock: {
          price: '12.5',
        },
      },
      isEvent: true,
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
    props.bookedPayload.quantity = 2

    // when
    const wrapper = shallow(<BookingSuccess {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should match the snapshot when booking a thing event', () => {
    // givn
    props.bookedPayload.quantity = 1
    props.isEvent = false

    // when
    const wrapper = shallow(<BookingSuccess {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
