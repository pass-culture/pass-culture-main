import React from 'react'
import { shallow } from 'enzyme'

import Footer from '../Footer'

describe('src | components | pages | search | Footer', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      // when
      const wrapper = shallow(<Footer />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
