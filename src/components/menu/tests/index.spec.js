import React from 'react'
import { shallow } from 'enzyme'

import MainMenu from '../index'

describe('src | components | menu | MainMenu', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: jest.fn(),
        isVisible: true,
      }

      // when
      const wrapper = shallow(<MainMenu {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
