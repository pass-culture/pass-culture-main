import React from 'react'
import { shallow } from 'enzyme'

import BookingLoader from '../BookingLoader'

<<<<<<< HEAD
describe('src | components | pages | search | BookingLoader', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      errors: {},
    }

=======
describe('src | components | layout | Booking | BookingLoader', () => {
  let props

  beforeEach(() => {
    props = {
      errors: {},
    }
  })

  it('should match snapshot', () => {
>>>>>>> (PC-2218): refactored BookingForm to make it testable
    // when
    const wrapper = shallow(<BookingLoader {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
