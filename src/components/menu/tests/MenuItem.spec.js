import React from 'react'
import { shallow } from 'enzyme'

import MenuItem, { MenuItemContent } from '../MenuItem'

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
})

describe('src | components | menu | MenuItem', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        item: {},
        location: {},
      }

      // when
      const wrapper = shallow(<MenuItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
