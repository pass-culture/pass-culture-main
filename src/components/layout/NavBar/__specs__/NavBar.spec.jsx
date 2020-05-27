import { mount, shallow } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import NavBar from '../NavBar'
import { isPathWithNavBar } from '../domain/isPathWithNavBar'

jest.mock('../domain/isPathWithNavBar')

describe('nav bar', () => {
  let props

  afterEach(() => {
    isPathWithNavBar.mockReset()
  })

  describe('when legitimed path', () => {
    beforeEach(() => {
      props = {
        path: '/path/with/navbar',
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

    it('should display a link to discovery page', () => {
      // When
      const wrapper = mount(
        <Router history={createMemoryHistory()}>
          <NavBar {...props} />
        </Router>
      )

      // Then
      const discoveryPageLink = wrapper.find('nav ul li a')
      expect(discoveryPageLink.at(0).prop('href')).toBe('/decouverte')
      expect(
        discoveryPageLink
          .at(0)
          .find('svg title')
          .text()
      ).toBe('Les offres')
    })

    it('should display a link to search page', () => {
      // When
      const wrapper = mount(
        <Router history={createMemoryHistory()}>
          <NavBar {...props} />
        </Router>
      )

      // Then
      const searchPageLink = wrapper.find('nav ul li a')
      expect(searchPageLink.at(1).prop('href')).toBe('/recherche')
      expect(
        searchPageLink
          .at(1)
          .find('svg title')
          .text()
      ).toBe('Recherche')
    })

    it('should display a link to bookings page', () => {
      // When
      const wrapper = mount(
        <Router history={createMemoryHistory()}>
          <NavBar {...props} />
        </Router>
      )

      // Then
      const bookingsPageLink = wrapper.find('nav ul li a')
      expect(bookingsPageLink.at(2).prop('href')).toBe('/reservations')
      expect(
        bookingsPageLink
          .at(2)
          .find('svg title')
          .text()
      ).toBe('Mes réservations')
    })

    it('should display a link to favorites page', () => {
      // When
      const wrapper = mount(
        <Router history={createMemoryHistory()}>
          <NavBar {...props} />
        </Router>
      )

      // Then
      const favoritesPageLink = wrapper.find('nav ul li a')
      expect(favoritesPageLink.at(3).prop('href')).toBe('/favoris')
      expect(
        favoritesPageLink
          .at(3)
          .find('svg title')
          .text()
      ).toBe('Mes favoris')
    })

    it('should display a link to my profile page', () => {
      // When
      const wrapper = mount(
        <Router history={createMemoryHistory()}>
          <NavBar {...props} />
        </Router>
      )

      // Then
      const profilePageLink = wrapper.find('nav ul li a')
      expect(profilePageLink.at(4).prop('href')).toBe('/profil')
      expect(
        profilePageLink
          .at(4)
          .find('svg title')
          .text()
      ).toBe('Mon compte')
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
