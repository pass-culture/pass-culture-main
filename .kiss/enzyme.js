// ./node_modules/.bin/jest --env=jsdom ./path/to/file.spec.js --watch
import React from 'react'
import { shallow } from 'enzyme'

import MyComponent from '../MyComponent'

describe('src | components | MyComponent', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = { errors: {} }
      // when
      const wrapper = shallow(<MyComponent {...props} />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
