import React from 'react'
import { shallow } from 'enzyme'

import Header from '../Header'

describe('src | components | Layout | Header', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given

      // when
      const wrapper = shallow(<Header />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
