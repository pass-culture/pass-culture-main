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
        push: jest.fn(),
      },
      match: {
        path: '/profil',
      },
      user: new User({
        email: 'beneficiary@example.com',
      }),
    }
  })

  describe('when current user has been fetched', () => {
    it('should allow redirection to specific routes', () => {
      // when
      const wrapper = shallow(<Profile {...props} />)

      // then
      const routes = wrapper.find(Route)
      expect(routes.at(0).prop('path')).toBe('/profil/mot-de-passe')
      expect(routes.at(1).prop('path')).toBe('/profil/informations')
      expect(routes.at(2).prop('path')).toBe('/profil/mentions-legales')
    })
  })
})
