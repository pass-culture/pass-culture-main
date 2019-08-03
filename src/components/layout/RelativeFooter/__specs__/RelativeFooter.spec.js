import React from 'react'
import { shallow } from 'enzyme'

import RelativeFooter from '../RelativeFooter'

describe('src | components | pages | RelativeFooter', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        theme: 'fakeTheme',
      }

      // when
      const wrapper = shallow(<RelativeFooter {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
