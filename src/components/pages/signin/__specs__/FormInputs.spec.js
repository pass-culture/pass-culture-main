import React from 'react'
import { shallow } from 'enzyme'

import FormInputs from '../FormInputs'

describe('src | components | pages | signin | FormInputs', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {}

      // when
      const wrapper = shallow(<FormInputs {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
