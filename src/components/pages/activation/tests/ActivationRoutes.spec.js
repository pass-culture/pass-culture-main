import React from 'react'
import { shallow } from 'enzyme'
import { Redirect, Route } from 'react-router'
import ActivationPageContainer from '../password/ActivationPageContainer'
import ActivationError from '../error'

import ActivationRoutes from '../ActivationRoutes'

describe('src | components | pages | activation | tests | index', () => {
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
      expect(routes.at(1).prop('path')).toBe('/activation/:token')
      expect(routes.at(1).prop('component')).toEqual(ActivationPageContainer)
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

    it('should redirect to error page when does not match any known URLs', () => {
      // given
      const wrapper = shallow(<ActivationRoutes />)

      // then
      const redirect = wrapper.find(Redirect)
      expect(redirect.prop('to')).toBe('/activation/error')
    })
})
