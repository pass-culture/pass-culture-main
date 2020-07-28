import { mount } from 'enzyme'
import React from 'react'

import { MemoryRouter } from 'react-router'
import NotMatch from '../NotMatch'
import { Link } from 'react-router-dom'
import Icon from '../../../layout/Icon/Icon'

describe('notMatch', () => {
  beforeEach(() => {
    window.history.pushState({}, 'Fake title', '/fake-url')
  })

  it('should displays a message notifying the user they are on a wrong path and a link to redirect', () => {
    // when
    const wrapper = mount(
      <MemoryRouter>
        <NotMatch />
      </MemoryRouter>
    )

    // then
    const icon = wrapper.find(Icon)
    const message = wrapper.find('.subtitle')
    const link = wrapper.find(Link)
    expect(icon).toHaveLength(1)
    expect(message).toHaveLength(1)
    expect(link).toHaveLength(1)
    expect(link.prop('to')).toBe('/')
  })

  it('should display a link to redirect to the redirect props url if not default', () => {
    // when
    let props = {
      redirect: '/mon/autre/url',
    }
    const wrapper = mount(
      <MemoryRouter>
        <NotMatch {...props} />
      </MemoryRouter>
    )

    // then
    const link = wrapper.find(Link)
    expect(link).toHaveLength(1)
    expect(link.prop('to')).toBe('/mon/autre/url')
  })
})
