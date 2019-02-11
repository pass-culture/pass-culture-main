import React from 'react'
import SignupPage from '../SignupPage'
import { shallow } from 'enzyme'

describe('src | components | pages | Signup', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        errors: {},
      }

      // when
      const wrapper = shallow(<SignupPage {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
