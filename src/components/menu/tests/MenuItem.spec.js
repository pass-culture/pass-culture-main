import React from 'react'
import { shallow } from 'enzyme'

import MenuItem from '../MenuItem'

describe('src | components | menu | MenuItem', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        item: {},
        location: {},
      }

      // when
      const wrapper = shallow(<MenuItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
