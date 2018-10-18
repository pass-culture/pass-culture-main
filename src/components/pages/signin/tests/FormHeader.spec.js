import React from 'react'
import { shallow } from 'enzyme'

import FormHeader from '../FormHeader'

describe('src | components | pages | signin | FormHeader', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      const wrapper = shallow(<FormHeader />)
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
