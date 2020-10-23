import { shallow } from 'enzyme'
import React from 'react'
import { Route } from 'react-router-dom/umd/react-router-dom'

import Logo from 'components/layout/Logo'

import Signup from '../Signup'

describe('src | components | pages | Signup', () => {
  it('should render logo and and two routes', () => {
    // given
    const props = {
      location: {},
    }

    // when
    const wrapper = shallow(<Signup {...props} />)

    // then
    const logo = wrapper.find(Logo)
    const routes = wrapper.find(Route)
    expect(logo).toHaveLength(1)
    expect(routes.at(1).prop('path')).toBe('/inscription/confirmation')
  })
})
