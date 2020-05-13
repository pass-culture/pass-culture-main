import React from 'react'
import { shallow } from 'enzyme'
import { Route } from 'react-router-dom'

import LoaderContainer from '../../../layout/Loader/LoaderContainer'
import Profile from '../Profile'

describe('profile page', () => {
  let props

  beforeEach(() => {
    props = {
      currentUser: {},
      location: {},
    }
  })

  describe('when current user has not been fetched yet', () => {
    it('should display a loading layout', () => {
      // given
      props.currentUser = undefined

      // when
      const wrapper = shallow(<Profile {...props} />)

      // then
      const loadingLayout = wrapper.find(LoaderContainer)
      expect(loadingLayout).toHaveLength(1)
    })
  })

  describe('when current user has been fetched', () => {
    it('should allow redirection to specific routes', () => {
      // given
      props.currentUser = {}

      // when
      const wrapper = shallow(<Profile {...props} />)

      // then
      const routes = wrapper.find(Route)
      expect(routes.at(0).prop('path')).toBe('/profil/:menu(menu)?')
      expect(routes.at(1).prop('path')).toBe('/profil/:view(mot-de-passe)/success/:menu(menu)?')
      expect(routes.at(2).prop('path')).toBe('/profil/:view(mot-de-passe)/:menu(menu)?')
      expect(routes.at(3).prop('path')).toBe('/profil/:view(informations)/:menu(menu)?')
    })
  })
})
