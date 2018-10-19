import React from 'react'
import { shallow } from 'enzyme'

import Splash from '../Splash'

describe('src | components | layout | Splash', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      const wrapper = shallow(<Splash />)
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
