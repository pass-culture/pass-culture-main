import React from 'react'
import { shallow } from 'enzyme'

import BookingError from '../BookingError'

<<<<<<< HEAD
describe('src | components | pages | search | BookingError', () => {
  it('should match the snapshot', () => {
    // given
    const errors = {}

    // when
    const wrapper = shallow(<BookingError errors={errors} />)

    // then
    expect(wrapper).toMatchSnapshot()
=======
describe('src | components | layout | Booking | BookingError', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const errors = {}

      // when
      const wrapper = shallow(<BookingError errors={errors} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
>>>>>>> (PC-2218): refactored BookingForm to make it testable
  })

  describe('render', () => {
    it('when errors is an array, does not output any messages', () => {
      // given
      const props = { errors: ['do not output something'] }

      // when
      const wrapper = shallow(<BookingError {...props} />)
<<<<<<< HEAD
      const list = wrapper.find('#booking-error-reasons p')
=======
>>>>>>> (PC-2218): refactored BookingForm to make it testable

      // then
      const list = wrapper.find('#booking-error-reasons p')
      expect(list).toHaveLength(1)
    })

    it('when errors is an object, does output some messages', () => {
      // given
      const props = {
        errors: {
          reason_1: ['Reason value 1'],
          reason_2: ['Reason value 2'],
          reason_34: ['Reason value 3', 'Reason value 4'],
        },
      }

      // when
      const wrapper = shallow(<BookingError {...props} />)
<<<<<<< HEAD
      const list = wrapper.find('#booking-error-reasons p')
=======
>>>>>>> (PC-2218): refactored BookingForm to make it testable

      // then
      const list = wrapper.find('#booking-error-reasons p')
      expect(list).toHaveLength(5)
      expect(list.at(1).text()).toStrictEqual('Reason value 1')
      expect(list.at(4).text()).toStrictEqual('Reason value 4')
    })
  })
})
