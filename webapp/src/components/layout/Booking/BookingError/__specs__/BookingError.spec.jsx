import { shallow } from 'enzyme'
import React from 'react'

import BookingError from '../BookingError'

describe('src | components | layout | Booking | BookingError', () => {
  describe('render', () => {
    it('when errors is an array, does not output any messages', () => {
      // given
      const props = { errors: ['do not output something'] }

      // when
      const wrapper = shallow(<BookingError {...props} />)

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

      // then
      const list = wrapper.find('#booking-error-reasons p')
      expect(list).toHaveLength(5)
      expect(list.at(1).text()).toStrictEqual('Reason value 1')
      expect(list.at(4).text()).toStrictEqual('Reason value 4')
    })
  })
})
