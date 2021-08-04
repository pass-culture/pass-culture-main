import { shallow } from 'enzyme'
import React from 'react'
import { Route } from 'react-router-dom'

import PageNotFoundContainer from '../../layout/ErrorBoundaries/ErrorsPage/PageNotFound/PageNotFoundContainer'
import FeaturedRoute from '../FeaturedRoute'

const Foo = () => <div />

describe('src | components | router | FeaturedRoute', () => {
  describe('when features are not yet loaded', () => {
    it('should render null', () => {
      // given
      const props = {
        areFeaturesLoaded: false,
        component: Foo,
        isRouteDisabled: false,
        featuresFetchFailed: false,
        requestGetFeatures: jest.fn(),
        handleRequestCategories: jest.fn(),
      }

      // when
      const wrapper = shallow(<FeaturedRoute {...props} />)

      // then
      const routeWrapper = wrapper.find(Route)
      expect(routeWrapper).toHaveLength(0)
    })

    it('should call requestGetFeatures', () => {
      // given
      const props = {
        areFeaturesLoaded: false,
        component: Foo,
        isRouteDisabled: false,
        requestGetFeatures: jest.fn(),
        handleRequestCategories: jest.fn(),
      }

      // when
      shallow(<FeaturedRoute {...props} />)

      // then
      expect(props.requestGetFeatures).toHaveBeenCalledTimes(1)
    })
  })

  describe('when features are loaded and disabled', () => {
    it('should render NotMatch', () => {
      // given
      const props = {
        areFeaturesLoaded: true,
        component: Foo,
        isRouteDisabled: true,
        featuresFetchFailed: false,
        requestGetFeatures: jest.fn(),
      }

      // when
      const wrapper = shallow(<FeaturedRoute {...props} />)

      // then
      const routeWrapper = wrapper.find(Route)
      expect(routeWrapper).toHaveLength(1)
      expect(routeWrapper.props().component).toBe(PageNotFoundContainer)
      expect(props.requestGetFeatures).toHaveBeenCalledTimes(0)
    })

    it('should not call requestGetFeatures', () => {
      // given
      const props = {
        areFeaturesLoaded: true,
        component: Foo,
        isRouteDisabled: true,
        featuresFetchFailed: false,
        requestGetFeatures: jest.fn(),
      }

      // when
      shallow(<FeaturedRoute {...props} />)

      // then
      expect(props.requestGetFeatures).toHaveBeenCalledTimes(0)
    })
  })

  describe('when features are loaded and not disabled', () => {
    it('should render Foo', () => {
      // given
      const props = {
        areFeaturesLoaded: true,
        component: Foo,
        isRouteDisabled: false,
        featuresFetchFailed: false,
        requestGetFeatures: jest.fn(),
      }

      // when
      const wrapper = shallow(<FeaturedRoute {...props} />)

      // then
      const routeWrapper = wrapper.find(Route)
      expect(routeWrapper).toHaveLength(1)
      expect(routeWrapper.props().component).toBe(Foo)
      expect(props.requestGetFeatures).toHaveBeenCalledTimes(0)
    })

    it('should not call requestGetFeatures', () => {
      // given
      const props = {
        areFeaturesLoaded: true,
        component: Foo,
        isRouteDisabled: false,
        featuresFetchFailed: false,
        requestGetFeatures: jest.fn(),
      }

      // when
      shallow(<FeaturedRoute {...props} />)

      // then
      expect(props.requestGetFeatures).toHaveBeenCalledTimes(0)
    })
  })

  describe('when feature fetch has failed', () => {
    it('should not call requestGetFeatures when feature fetch has failed', () => {
      // given
      const props = {
        areFeaturesLoaded: false,
        component: Foo,
        isRouteDisabled: true,
        featuresFetchFailed: true,
        requestGetFeatures: jest.fn(),
      }

      // when
      shallow(<FeaturedRoute {...props} />)

      // then
      expect(props.requestGetFeatures).toHaveBeenCalledTimes(0)
    })

    it('should render null by default', () => {
      // given
      const props = {
        areFeaturesLoaded: false,
        component: Foo,
        isRouteDisabled: false,
        featuresFetchFailed: true,
        requestGetFeatures: jest.fn(),
      }

      // when
      const wrapper = shallow(<FeaturedRoute {...props} />)

      // then
      const routeWrapper = wrapper.find(Route)
      expect(routeWrapper).toHaveLength(0)
    })

    it('should render Foo on the right path', () => {
      // given
      const props = {
        areFeaturesLoaded: false,
        component: Foo,
        isRouteDisabled: false,
        featuresFetchFailed: true,
        requestGetFeatures: jest.fn(),
        path: '/',
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
})
