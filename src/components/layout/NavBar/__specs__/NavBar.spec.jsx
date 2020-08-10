import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import NavBar from '../NavBar'

const icon = () => <svg />

describe('nav bar', () => {
  let props

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
})
