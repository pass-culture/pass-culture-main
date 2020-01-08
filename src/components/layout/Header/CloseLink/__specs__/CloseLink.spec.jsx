import { shallow } from 'enzyme'
import React from 'react'
import CloseLink from '../CloseLink'
import { Link } from 'react-router-dom'
import Icon from '../../../Icon/Icon'

describe('src | components | layout | Header | CloseLink', () => {
  let props

  beforeEach(() => {
    props = {
      actionOnClick: null,
      closeTitle: 'fake close title',
      closeTo: '/fake-url',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<CloseLink {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should display a Link component with the right props', () => {
      // when
      const wrapper = shallow(<CloseLink {...props} />)

      // then
      const link = wrapper.find(Link)
      expect(link).toHaveLength(1)
      expect(link.prop('className')).toBe('close-link')
      expect(link.prop('onClick')).toBeNull()
      expect(link.prop('to')).toBe('/fake-url')
    })

    it('should display an Icon component with the right props', () => {
      // when
      const wrapper = shallow(<CloseLink {...props} />)

      // then
      const icon = wrapper.find(Icon)
      expect(icon).toHaveLength(1)
      expect(icon.prop('alt')).toBe('fake close title')
      expect(icon.prop('className')).toBe('close-link-img')
      expect(icon.prop('svg')).toBe('ico-close-white')
    })
  })
})
