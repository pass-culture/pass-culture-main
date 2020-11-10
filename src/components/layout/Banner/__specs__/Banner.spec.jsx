import { shallow } from 'enzyme'
import React from 'react'

import Banner from '../Banner'

describe('src | components | layout | Banner', () => {
  describe('render', () => {
    let props = {
      subtitle: 'subtitle',
      href: '/some/site',
      linkTitle: 'linkTitle',
    }

    it('should render the Banner with the default props', () => {
      // when
      const wrapper = shallow(<Banner {...props} />)

      // then
      const subtitleComponent = wrapper.find({ children: 'subtitle' })
      expect(subtitleComponent).toHaveLength(1)

      const linkToHref = wrapper.find('a')
      expect(linkToHref.prop('href')).toBe(props.href)

      const icon = wrapper.find('Icon')
      expect(icon.prop('svg')).toBe('ico-external-site')
      expect(linkToHref.text()).toContain('linkTitle')
    })

    it('should change the banner type - attention', () => {
      // when
      const wrapper = shallow(<Banner {...props} />)

      // then
      const container = wrapper.find('div')
      expect(container.prop('className')).toBe('bi-banner attention')
    })

    it('should change the banner type - notification-info', () => {
      props.type = 'notification-info'

      // when
      const wrapper = shallow(<Banner {...props} />)

      // then
      const container = wrapper.find('div')
      expect(container.prop('className')).toBe('bi-banner notification-info')
    })
  })
})
