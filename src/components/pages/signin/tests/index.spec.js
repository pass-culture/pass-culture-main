import React from 'react'
import { shallow } from 'enzyme'

import Index from '../index'

describe('src | components | pages | signin | Index', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {}

      // when
      const wrapper = shallow(<Index {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
