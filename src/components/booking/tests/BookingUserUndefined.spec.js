import React from 'react'
import { shallow } from 'enzyme'

import BookingUserUndefined from '../BookingUserUndefined'

describe('src | components | pages | search | BookingUserUndefined', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        show: true,
      }

      // when
      const wrapper = shallow(<BookingUserUndefined {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
