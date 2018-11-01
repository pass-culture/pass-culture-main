import React from 'react'
import SigninPage from '../SigninPage'
import { shallow } from 'enzyme'

describe('src | components | pages | SigninPage', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        errors: {},
      }

      // when
      const wrapper = shallow(<SigninPage {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
