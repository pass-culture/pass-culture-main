import { shallow } from 'enzyme'
import React from 'react'
import ExternalLink from '../ExternalLink'
import Icon from '../../../../../layout/Icon/Icon'

describe('external link component', () => {
  let props
  beforeEach(() => {
    props = {
      href: 'http://example.com',
      icon: 'ico-test',
      title: 'Title URL',
      label: 'Link Label',
    }
  })

  it('should display an external link', () => {
    // When
    const wrapper = shallow(<ExternalLink {...props} />)

    // Then
    const externalLink = wrapper.find({ children: 'Link Label' }).parent()

    const externalLinkIcon = wrapper.find(Icon)

    expect(externalLink.prop('href')).toBe('http://example.com')
    expect(externalLink.prop('title')).toBe('Title URL')
    expect(externalLinkIcon).toHaveLength(2)
  })
})
