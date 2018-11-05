import React from 'react'
import { shallow } from 'enzyme'

import App from '../App'

describe.skip('src | components | share | App', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {}
      // when
      const wrapper = shallow(<App {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
