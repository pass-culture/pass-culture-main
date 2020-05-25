import { shallow } from 'enzyme'
import React from 'react'
import { Route } from 'react-router-dom'

import Profile from '../Profile'
import User from '../ValueObjects/User'

describe('profile page', () => {
  let props

  beforeEach(() => {
    props = {
      history: {
        push: jest.fn()
      },
      location: {},
      user: new User({
        email: 'toto@example.com',
        id: 'ABC123'
      })
    }
  })

  describe('when current user has been fetched', () => {
    it('should allow redirection to specific routes', () => {
      // when
      const wrapper = shallow(<Profile {...props} />)

      // then
      const routes = wrapper.find(Route)
      expect(routes.at(0).prop('path')).toBe('/profil/:menu(menu)?')
      expect(routes.at(1).prop('path')).toBe('/profil/:view(mot-de-passe)/:menu(menu)?')
      expect(routes.at(2).prop('path')).toBe('/profil/:view(informations)/:menu(menu)?')
    })
  })
})
