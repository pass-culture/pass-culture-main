import { shallow } from 'enzyme'
import React from 'react'

import SigninContainer from '../SigninContainer'

describe('src | components | pages | signin | Index', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {}

      // when
      const wrapper = shallow(<SigninContainer {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
