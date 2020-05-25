import { shallow } from 'enzyme'
import React from 'react'
import Icon from '../../../../layout/Icon/Icon'
import InternalLink from '../InternalLink'

describe('internal link component', () => {
  let props
  beforeEach(() => {
    props = {
      to: 'http://example.com',
      icon: 'ico-test',
      label: 'Link Label',
    }
  })

  it('should display an internal link', () => {
    // When
    const wrapper = shallow(<InternalLink {...props} />)

    // Then
    const internalLink = wrapper.find({ children: 'Link Label' }).parent()

    const internalLinkIcon = wrapper.find(Icon)

    expect(internalLink.prop('to')).toBe('http://example.com')
    expect(internalLinkIcon).toHaveLength(2)
  })
})
