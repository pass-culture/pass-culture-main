import { shallow } from 'enzyme'
import React from 'react'

import Banner from '../Banner'

describe('src | components | layout | Banner', () => {
  describe('render', () => {
    it('should render the Banner with the correct props', () => {
      // given
      const props = {
        subtitle: 'subtitle',
        href: 'href',
        linkTitle: 'linkTitle',
      }

      // when
      const wrapper = shallow(<Banner {...props} />)

      // then
      const subtitleComponent = wrapper.find({ children: 'subtitle' })
      expect(subtitleComponent).toHaveLength(1)

      const linkToHref = wrapper.find('a')
      expect(linkToHref.prop('href')).toBe('href')

      const icon = wrapper.find('Icon')
      expect(icon.prop('svg')).toBe('ico-external-site') // by default
      expect(linkToHref.text()).toContain('linkTitle')
    })
  })
})
