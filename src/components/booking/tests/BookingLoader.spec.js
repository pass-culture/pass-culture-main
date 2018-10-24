import React from 'react'
import { shallow } from 'enzyme'

import BookingLoader from '../BookingLoader'

describe('src | components | pages | search | BookingLoader', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        errors: {},
      }

      // when
      const wrapper = shallow(<BookingLoader {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
