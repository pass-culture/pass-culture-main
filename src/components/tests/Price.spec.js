import React from 'react'
import { shallow } from 'enzyme'

import Price from '../Price'

describe('src | components | pages | Price', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {}

      // when
      const wrapper = shallow(<Price {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
