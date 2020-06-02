import { mount, shallow } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import NavBar from '../NavBar'
import { isPathWithNavBar } from '../domain/isPathWithNavBar'

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
        path: '/path/with/navbar',
        routes: [
          {
            icon,
            to: '/first-path',
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
      const wrapper = shallow(<NavBar {...props} />)

      // Then
      const navBar = wrapper.find('nav')
      expect(navBar).toHaveLength(1)
      expect(isPathWithNavBar).toHaveBeenCalledWith(props.path)
    })

    it('should display the first link', () => {
      // When
      const wrapper = mount(
        <Router history={createMemoryHistory()}>
          <NavBar {...props} />
        </Router>
      )

      // Then
      const discoveryPageLink = wrapper.find('nav ul li a')
      expect(discoveryPageLink.at(0).prop('href')).toBe('/first-path')
      expect(discoveryPageLink.at(1).find('svg')).toHaveLength(1)
    })

    it('should display the second link', () => {
      // When
      const wrapper = mount(
        <Router history={createMemoryHistory()}>
          <NavBar {...props} />
        </Router>
      )

      // Then
      const searchPageLink = wrapper.find('nav ul li a')
      expect(searchPageLink.at(1).prop('href')).toBe('/second-path')
      expect(searchPageLink.at(1).find('svg')).toHaveLength(1)
    })
  })

  describe('when forbiden path', () => {
    it('should not display navbar', () => {
      // Given
      props.path = '/path/without/navbar'
      isPathWithNavBar.mockReturnValue(false)

      // When
      const wrapper = shallow(<NavBar {...props} />)

      // Then
      const navBar = wrapper.find('nav')
      expect(navBar).toHaveLength(0)
      expect(isPathWithNavBar).toHaveBeenCalledWith(props.path)
    })
  })
})
