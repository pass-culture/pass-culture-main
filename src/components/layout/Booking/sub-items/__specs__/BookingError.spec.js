import React from 'react'
import { shallow } from 'enzyme'

import BookingError from '../BookingError'

describe('src | components | pages | search | BookingError', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const errors = {}
      const wrapper = shallow(<BookingError errors={errors} />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    it('when errors is an array, does not output any messages', () => {
      // given
      const props = { errors: ['do not output something'] }
      // when
      const wrapper = shallow(<BookingError {...props} />)
      const list = wrapper.find('#booking-error-reasons p')
      // then
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
      const list = wrapper.find('#booking-error-reasons p')
      // then
      expect(list).toHaveLength(5)
      expect(list.at(1).text()).toStrictEqual('Reason value 1')
      expect(list.at(4).text()).toStrictEqual('Reason value 4')
    })
  })
})
