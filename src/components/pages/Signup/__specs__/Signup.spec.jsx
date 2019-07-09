import { shallow } from 'enzyme'
import React from 'react'

import Signup from '../Signup'

describe('src | components | pages | Signup', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        errors: {},
      }

      // when
      const wrapper = shallow(<Signup {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
