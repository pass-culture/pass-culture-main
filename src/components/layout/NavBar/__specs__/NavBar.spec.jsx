import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import NavBar from '../NavBar'

const icon = () => <svg />

describe('nav bar', () => {
  let props

  beforeEach(() => {
    props = {
      isFeatureEnabled: jest.fn(),
      routes: [
        {
          icon,
          to: '/first-path',
          featureName: 'FEATURE_NAME_1',
        },
        {
          icon,
          to: '/second-path',
          featureName: 'FEATURE_NAME_2',
        },
      ],
    }
  })

  it('should display the first link when feature is enabled for first route only', () => {
    // given
    props.isFeatureEnabled
      .mockReturnValueOnce(true)
      .mockReturnValueOnce(false)

    // when
    const wrapper = mount(
      <MemoryRouter>
        <NavBar {...props} />
      </MemoryRouter>,
    )

    // then
    const allLinks = wrapper.find('nav ul li a')
    expect(allLinks).toHaveLength(1)
    expect(allLinks.at(0).prop('href')).toBe('/first-path')
    expect(allLinks.at(0).find('svg')).toHaveLength(1)
  })

  it('should display the second link when feature is enabled for second route only', () => {
    // given
    props.isFeatureEnabled
      .mockReturnValueOnce(false)
      .mockReturnValueOnce(true)

    // when
    const wrapper = mount(
      <MemoryRouter>
        <NavBar {...props} />
      </MemoryRouter>,
    )

    // then
    const allLinks = wrapper.find('nav ul li a')
    expect(allLinks).toHaveLength(1)
    expect(allLinks.at(0).prop('href')).toBe('/second-path')
    expect(allLinks.at(0).find('svg')).toHaveLength(1)
  })

  it('should display all links when there is no notion of feature flipping', () => {
    // given
    props.routes = [
      { icon, to: '/first-path' },
      { icon, to: '/second-path' },
    ]
    props.isFeatureEnabled
      .mockReturnValueOnce(true)
      .mockReturnValueOnce(true)

    // when
    const wrapper = mount(
      <MemoryRouter>
        <NavBar {...props} />
      </MemoryRouter>,
    )

    // then
    const allLinks = wrapper.find('nav ul li a')
    expect(allLinks).toHaveLength(2)
    expect(allLinks.at(0).prop('href')).toBe('/first-path')
    expect(allLinks.at(0).find('svg')).toHaveLength(1)
    expect(allLinks.at(1).prop('href')).toBe('/second-path')
    expect(allLinks.at(1).find('svg')).toHaveLength(1)
  })

  it('should not display any links when feature is disabled for all routes', () => {
    // given
    props.isFeatureEnabled
      .mockReturnValueOnce(false)
      .mockReturnValueOnce(false)

    // when
    const wrapper = mount(
      <MemoryRouter>
        <NavBar {...props} />
      </MemoryRouter>,
    )

    // then
    const allLinks = wrapper.find('nav ul li a')
    expect(allLinks).toHaveLength(0)
  })
})
