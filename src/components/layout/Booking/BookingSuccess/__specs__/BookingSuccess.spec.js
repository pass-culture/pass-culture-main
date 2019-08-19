import React from 'react'
import { shallow } from 'enzyme'

import BookingSuccess from '../BookingSuccess'

<<<<<<< HEAD
describe('src | components | pages | search | BookingSuccess', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      data: {
        token: 'G8G8G8',
      },
      isEvent: true,
    }

=======
describe('src | components | layout | Booking | BookingSuccess', () => {
  let props

  beforeEach(() => {
    props = {
      data: {
        token: 'G8G8G8',
      },
      isEvent: true,
    }
  })

  it('should match snapshot', () => {
>>>>>>> (PC-2218): refactored BookingForm to make it testable
    // when
    const wrapper = shallow(<BookingSuccess {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
