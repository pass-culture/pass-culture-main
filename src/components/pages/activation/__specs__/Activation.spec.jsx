import { shallow } from 'enzyme'
import React from 'react'
import { Redirect, Route } from 'react-router'

import Activation from '../Activation'
import Error from '../Error/Error'
import InvalidLink from '../InvalidLink/InvalidLink'
import PasswordFormContainer from '../PasswordForm/PasswordFormContainer'

describe('activation', () => {
  it('should render route for activating password when token is given', () => {
    // when
    const wrapper = shallow(<Activation />)

    // then
    const routes = wrapper.find(Route)
    const passwordFormContainer = wrapper.find(PasswordFormContainer)
    expect(routes.at(2).prop('path')).toBe('/activation/:token([A-Z0-9]+)')
    expect(passwordFormContainer).toHaveLength(1)
  })

  it('should render error component when route is exactly /activation/error', () => {
    // given
    const wrapper = shallow(<Activation />)

    // then
    const routes = wrapper.find(Route)
    const error = wrapper.find(Error)
    expect(routes.at(0).prop('path')).toBe('/activation/error')
    expect(error).toHaveLength(1)
    expect(routes.at(0).prop('exact')).toBeDefined()
  })

  it('should redirect to error page when current URLs does not match any mapped URLs', () => {
    // given
    const wrapper = shallow(<Activation />)

    // then
    const redirect = wrapper.find(Redirect)
    expect(redirect.prop('to')).toBe('/activation/error')
  })

  it('should render InvalidLink component when route is exactly /activation/lien-invalide', () => {
    // given
    const wrapper = shallow(<Activation />)

    // then
    const routes = wrapper.find(Route)
    const invalidLink = wrapper.find(InvalidLink)
    expect(routes.at(1).prop('path')).toBe('/activation/lien-invalide')
    expect(invalidLink).toHaveLength(1)
    expect(routes.at(1).prop('exact')).toBeDefined()
  })
})
