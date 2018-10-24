import React from 'react'
import { shallow } from 'enzyme'

import BookingError from '../BookingError'

describe('src | components | pages | search | BookingError', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        errors: {},
      }

      // when
      const wrapper = shallow(<BookingError {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
