import React from 'react'
import { shallow } from 'enzyme'

import MyComponent from '../MyComponent'

describe('src | components | MyComponent', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      const props = { errors: {} }
      const wrapper = shallow(<MyComponent {...props} />)
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
