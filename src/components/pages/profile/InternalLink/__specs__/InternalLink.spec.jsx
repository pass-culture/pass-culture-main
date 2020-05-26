import React from 'react'
import { Router } from 'react-router-dom'
import { mount } from 'enzyme'
import { createMemoryHistory } from 'history'

import Icon from '../../../../layout/Icon/Icon'
import InternalLink from '../InternalLink'

describe('internal link component', () => {
  let props
  beforeEach(() => {
    props = {
      to: '/page',
      icon: 'ico-test',
      label: 'Link Label',
    }
  })

  it('should display an internal link', () => {
    // When
    const wrapper = mount(
      <Router history={createMemoryHistory()}>
        <InternalLink {...props} />
      </Router>
    )

    // Then
    const internalLink = wrapper.find({ children: 'Link Label' }).parent()
    const internalLinkIcon = wrapper.find(Icon)
    expect(internalLink.prop('href')).toBe('/page')
    expect(internalLinkIcon).toHaveLength(2)
  })
})
