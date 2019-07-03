import { shallow } from 'enzyme'
import React from 'react'
import { Route } from 'react-router-dom'

import FeaturedRoute from '../FeaturedRoute'
import NotMatch from '../../pages/NotMatch'

const Foo = () => <div />

describe('src | components | router | FeaturedRoute', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      component: Foo,
      features: [{ name: 'FOO' }],
      requestGetFeatures: jest.fn()
    }

    // when
    const wrapper = shallow(<FeaturedRoute {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should render null when no features', () => {
    // given
    const props = {
      component: Foo,
      features: null,
      requestGetFeatures: jest.fn()
    }

    // when
    const wrapper = shallow(<FeaturedRoute {...props} />)

    // then
    const routeWrapper = wrapper.find(Route)
    expect(routeWrapper).toHaveLength(0)
    expect(props.requestGetFeatures).toHaveBeenCalledTimes(1)
  })

  it('should render NotMatch when features and isFeatureDisabled', () => {
    // given
    const props = {
      component: Foo,
      isFeatureDisabled: true,
      features: [{ name: 'FOO' }],
      requestGetFeatures: jest.fn()
    }

    // when
    const wrapper = shallow(<FeaturedRoute {...props} />)

    // then
    const routeWrapper = wrapper.find(Route)
    expect(routeWrapper).toHaveLength(1)
    expect(routeWrapper.props().component).toBe(NotMatch)
    expect(props.requestGetFeatures).toHaveBeenCalledTimes(0)
  })

  it('should render Foo when features and not isFeatureDisabled', () => {
    // given
    const props = {
      component: Foo,
      isFeatureDisabled: false,
      features: [{ name: 'FOO' }],
      requestGetFeatures: jest.fn()
    }

    // when
    const wrapper = shallow(<FeaturedRoute {...props} />)

    // then
    const routeWrapper = wrapper.find(Route)
    expect(routeWrapper).toHaveLength(1)
    expect(routeWrapper.props().component).toBe(Foo)
    expect(props.requestGetFeatures).toHaveBeenCalledTimes(0)
  })
})
