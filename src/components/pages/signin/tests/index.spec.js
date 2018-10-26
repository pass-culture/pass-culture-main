import React from 'react'
import { shallow } from 'enzyme'

import Signin from '../index'

describe('src | components | pages | signin | index', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: jest.fn(),
        history: {},
      }

      // when
      const wrapper = shallow(<Signin {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
