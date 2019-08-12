import React from 'react'
import { shallow } from 'enzyme'

import FormHeader from '../FormHeader'

describe('src | components | pages | signin | FormHeader', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {}

      // when
      const wrapper = shallow(<FormHeader {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
