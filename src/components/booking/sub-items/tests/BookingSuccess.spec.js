import React from 'react'
import { shallow } from 'enzyme'

import BookingSuccess from '../BookingSuccess'

describe('src | components | pages | search | BookingSuccess', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        data: {},
        isEvent: true,
      }

      // when
      const wrapper = shallow(<BookingSuccess {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
