import React from 'react'
import { shallow } from 'enzyme'
import { Redirect, Route } from 'react-router'
import ActivationPageContainer from '../password/ActivationPageContainer'
import ActivationError from '../error/ActivationError'
import InvalidLink from '../invalid-link/InvalidLink'

import ActivationRoutes from '../ActivationRoutes'

describe('src | components | pages | activation | tests | ActivationRoutes', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<ActivationRoutes />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should render route for activating password when token is given', () => {
    // when
    const wrapper = shallow(<ActivationRoutes />)

    // then
    const routes = wrapper.find(Route)
    expect(routes.at(2).prop('path')).toBe('/activation/:token')
    expect(routes.at(2).prop('component')).toEqual(ActivationPageContainer)
  })

  it('should render error component when route is exactly /activation/error', () => {
    // given
    const wrapper = shallow(<ActivationRoutes />)

    // then
    const routes = wrapper.find(Route)
    expect(routes.at(0).prop('path')).toBe('/activation/error')
    expect(routes.at(0).prop('component')).toEqual(ActivationError)
    expect(routes.at(0).prop('exact')).toBeDefined()
  })

  it('should redirect to error page when current URLs does not match any mapped URLs', () => {
    // given
    const wrapper = shallow(<ActivationRoutes />)

    // then
    const redirect = wrapper.find(Redirect)
    expect(redirect.prop('to')).toBe('/activation/error')
  })

  it('should render InvalidLink component when route is exactly /activation/lien-invalide', () => {
    // given
    const wrapper = shallow(<ActivationRoutes />)

    // then
    const routes = wrapper.find(Route)
    expect(routes.at(1).prop('path')).toBe('/activation/lien-invalide')
    expect(routes.at(1).prop('component')).toEqual(InvalidLink)
    expect(routes.at(1).prop('exact')).toBeDefined()
  })
})
