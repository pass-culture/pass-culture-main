import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { isPathWithNavBar } from '../domain/isPathWithNavBar'
import NavBar from '../NavBar'

jest.mock('../domain/isPathWithNavBar')

const icon = () => <svg />

describe('nav bar', () => {
  let props

  afterEach(() => {
    isPathWithNavBar.mockReset()
  })

  describe('when legitimed path', () => {
    beforeEach(() => {
      props = {
        isFeatureEnabled: jest.fn(),
        path: '/path/with/navbar',
        routes: [
          {
            icon,
            to: '/first-path',
            featureName: 'FEATURE_NAME',
          },
          {
            icon,
            to: '/second-path',
          },
        ],
      }
      isPathWithNavBar.mockReturnValue(true)
    })

    it('should display navbar', () => {
      // When
      const wrapper = mount(
        <MemoryRouter>
          <NavBar {...props} />
        </MemoryRouter>
      )

      // Then
      const navBar = wrapper.find('nav')
      expect(navBar).toHaveLength(1)
      expect(isPathWithNavBar).toHaveBeenCalledWith(props.path)
    })

    describe('when feature is enabled', () => {
      beforeEach(() => {
        props.isFeatureEnabled.mockReturnValue(true)
      })

      it('should display the first link', () => {
        // When
        const wrapper = mount(
          <MemoryRouter>
            <NavBar {...props} />
          </MemoryRouter>
        )

        // Then
        const discoveryPageLink = wrapper.find('nav ul li a')
        expect(discoveryPageLink.at(0).prop('href')).toBe('/first-path')
        expect(discoveryPageLink.at(1).find('svg')).toHaveLength(1)
      })

      it('should display the second link', () => {
        // When
        const wrapper = mount(
          <MemoryRouter>
            <NavBar {...props} />
          </MemoryRouter>
        )

        // Then
        const searchPageLink = wrapper.find('nav ul li a')
        expect(searchPageLink.at(1).prop('href')).toBe('/second-path')
        expect(searchPageLink.at(1).find('svg')).toHaveLength(1)
      })
    })

    describe('when feature is disabled', () => {
      beforeEach(() => {
        props.isFeatureEnabled.mockReturnValue(false)
      })

      it('should not display the link', () => {
        // When
        const wrapper = mount(
          <MemoryRouter>
            <NavBar {...props} />
          </MemoryRouter>
        )

        // Then
        const discoveryPageLink = wrapper.find('nav ul li a')
        expect(discoveryPageLink).toHaveLength(0)
        expect(props.isFeatureEnabled).toHaveBeenCalledWith('FEATURE_NAME')
      })
    })
  })

  describe('when forbiden path', () => {
    it('should not display navbar', () => {
      // Given
      props.path = '/path/without/navbar'
      isPathWithNavBar.mockReturnValue(false)

      // When
      const wrapper = mount(
        <MemoryRouter>
          <NavBar {...props} />
        </MemoryRouter>
      )

      // Then
      const navBar = wrapper.find('nav')
      expect(navBar).toHaveLength(0)
      expect(isPathWithNavBar).toHaveBeenCalledWith(props.path)
    })
  })

  describe('when the current path starts with the route', () => {
    it('should transform link into non link', () => {
      // Given
      props = {
        isFeatureEnabled: jest.fn(() => true),
        path: '/the/same/path/ME/FA',
        routes: [
          {
            icon,
            to: '/the/same/path',
          },
          {
            icon,
            to: '/second-path',
          },
        ],
      }
      isPathWithNavBar.mockReturnValue(true)

      // When
      const wrapper = mount(
        <MemoryRouter>
          <NavBar {...props} />
        </MemoryRouter>
      )

      // Then
      const navBarList = wrapper.find('nav').find('li')
      expect(navBarList.at(0).find('a')).toHaveLength(0)
      expect(navBarList.at(1).find('a')).toHaveLength(1)
    })
  })
})
