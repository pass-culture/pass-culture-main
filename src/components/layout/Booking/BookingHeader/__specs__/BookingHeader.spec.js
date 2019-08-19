import React from 'react'
import { shallow } from 'enzyme'

import BookingHeader from '../BookingHeader'

<<<<<<< HEAD
describe('src | components | booking | BookingHeader', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
=======
describe('src | components | layout | Booking | BookingHeader ', () => {
  let props

  beforeEach(() => {
    props = {
>>>>>>> (PC-2218): refactored BookingForm to make it testable
      recommendation: {
        offer: {
          name: 'Titre de la recommendation',
          product: { name: 'Titre de la recommendation' },
          venue: { name: 'Titre de la venue ' },
        },
      },
    }
<<<<<<< HEAD

=======
  })

  it('should match snapshot', () => {
>>>>>>> (PC-2218): refactored BookingForm to make it testable
    // when
    const wrapper = shallow(<BookingHeader {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
