import React from 'react'
import { shallow } from 'enzyme'

import MenuItemContent from '../MenuItemContent'

describe('src | components | menu | MenuItemContent', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        clickHandler: jest.fn(),
        item: {},
        location: {},
      }

      // when
      const wrapper = shallow(<MenuItemContent {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    describe('functions', () => {
      describe('renderNavLink', () => {})
      describe('renderSimpleLink', () => {})
    })
  })
})
