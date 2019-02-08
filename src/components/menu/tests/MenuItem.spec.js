// jest --env=jsdom ./src/components/menu/tests/MenuItem --watch
import React from 'react'
import { shallow } from 'enzyme'

import MenuItem, { MenuItemContent } from '../MenuItem'

const routerProps = {
  location: { pathname: '/decouverte' },
}

describe('src | components | menu | MenuItemContent', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        ...routerProps,
        clickHandler: jest.fn(),
        item: { path: '/decouverte' },
        match: { params: {} },
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
    it('should match snapshot with in-app link', () => {
      // given
      const props = {
        ...routerProps,
        item: { path: '/decouverte' },
      }

      // when
      const wrapper = shallow(<MenuItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
    it('should match snapshot with external link', () => {
      // given
      const props = {
        ...routerProps,
        item: { href: 'http://www.external.link', target: '_blank' },
      }

      // when
      const wrapper = shallow(<MenuItem {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
