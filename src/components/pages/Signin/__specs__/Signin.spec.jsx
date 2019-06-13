import React from 'react'
import Signin from '../Signin'
import { shallow } from 'enzyme'

describe('src | components | pages | Signin', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        errors: {},
      }

      // when
      const wrapper = shallow(<Signin {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
