import React from 'react'
import { shallow } from 'enzyme'
import { Redirect, Route } from 'react-router'

import PasswordFormContainer from '../PasswordForm/PasswordFormContainer'
import Error from '../Error'
import InvalidLink from '../InvalidLink'

import Activation from '../Activation'

describe('src | components | pages | activation | Activation', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Activation />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render route for activating password when token is given', () => {
    // when
    const wrapper = shallow(<Activation />)

    // then
    const routes = wrapper.find(Route)
    expect(routes.at(2).prop('path')).toBe('/activation/:token')
    expect(routes.at(2).prop('component')).toStrictEqual(PasswordFormContainer)
  })

  it('should render error component when route is exactly /activation/error', () => {
    // given
    const wrapper = shallow(<Activation />)

    // then
    const routes = wrapper.find(Route)
    expect(routes.at(0).prop('path')).toBe('/activation/error')
    expect(routes.at(0).prop('component')).toStrictEqual(Error)
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
    expect(routes.at(1).prop('path')).toBe('/activation/lien-invalide')
    expect(routes.at(1).prop('component')).toStrictEqual(InvalidLink)
    expect(routes.at(1).prop('exact')).toBeDefined()
  })
})
