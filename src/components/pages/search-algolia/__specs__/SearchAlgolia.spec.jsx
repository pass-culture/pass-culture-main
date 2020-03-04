import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Route, Router } from 'react-router'
import SearchAlgolia from '../SearchAlgolia'

describe('src | components | pages | search-algolia | SearchAlgolia', () => {
  describe('routing', () => {
    it('should render SearchHome page when path is exactly /recherche-offres', () => {
      // Given
      const wrapper = shallow(
        <SearchAlgolia
          history={createBrowserHistory()}
          isGeolocationEnabled={jest.fn()}
          location={{ pathname: 'recherche-offres', search: '' }}
          match={{
            params: {}
          }}
          query={{ clear: jest.fn(), change: jest.fn(), parse: jest.fn() }}
          redirectToSearchMainPage={jest.fn()}
        />
      )

      // When
      const routes = wrapper.find(Route)

      // Then
      expect(routes.at(0).prop('path')).toBe('/recherche-offres(/menu)?')
      expect(
        routes
          .at(0)
          .children()
          .type().name
      ).toStrictEqual('SearchHome')
      expect(routes.at(0).prop('exact')).toBeDefined()
    })

    it('should render SearchResults page when path is /recherche-offres/resultats', () => {
      // Given
      const wrapper = shallow(
        <SearchAlgolia
          history={createBrowserHistory()}
          isGeolocationEnabled={jest.fn()}
          location={{ pathname: 'recherche-offres/resultats', search: '' }}
          match={{
            params: {}
          }}
          query={{ clear: jest.fn(), change: jest.fn(), parse: jest.fn() }}
          redirectToSearchMainPage={jest.fn()}
        />
      )

      // When
      const routes = wrapper.find(Route)

      // Then
      expect(routes.at(1).prop('path')).toBe('/recherche-offres/resultats')
      expect(
        routes
          .at(1)
          .children()
          .type().name
      ).toStrictEqual('SearchResults')
    })

    it('should render GeolocationCriteria page when path is /recherche-offres/criteres-localisation', () => {
      // Given
      const wrapper = shallow(
        <SearchAlgolia
          history={createBrowserHistory()}
          isGeolocationEnabled={jest.fn()}
          location={{ pathname: 'recherche-offres/criteres-localisation', search: '' }}
          match={{
            params: {}
          }}
          query={{ clear: jest.fn(), change: jest.fn(), parse: jest.fn() }}
          redirectToSearchMainPage={jest.fn()}
        />
      )

      // When
      const routes = wrapper.find(Route)

      // Then
      expect(routes.at(2).prop('path')).toBe('/recherche-offres/criteres-localisation')
      expect(
        routes
          .at(2)
          .children()
          .type().name
      ).toStrictEqual('GeolocationCriteria')
    })
  })

  describe('when rendering', () => {
    it('should display "Autour de moi" if geolocation is enabled', () => {
      // Given
      const history = createBrowserHistory()
      history.location.pathname = '/recherche-offres'
      const wrapper = mount(
        <Router history={history}>
          <SearchAlgolia
            history={history}
            isGeolocationEnabled={jest.fn().mockReturnValue(true)}
            location={history.location}
            match={{ params: {} }}
            query={{ clear: jest.fn(), change: jest.fn(), parse: jest.fn() }}
            redirectToSearchMainPage={jest.fn()}
          />
        </Router>
      )

      // When
      const aroundMe = wrapper.findWhere(node => node.text() === 'Autour de moi').first()

      // Then
      expect(aroundMe).toHaveLength(1)
    })

    it('should display "Partout" if geolocation is disabled', () => {
      // Given
      const history = createBrowserHistory()
      history.location.pathname = '/recherche-offres'
      const wrapper = mount(
        <Router history={history}>
          <SearchAlgolia
            history={history}
            isGeolocationEnabled={jest.fn().mockReturnValue(false)}
            location={history.location}
            match={{ params: {} }}
            query={{ clear: jest.fn(), change: jest.fn(), parse: jest.fn() }}
            redirectToSearchMainPage={jest.fn()}
          />
        </Router>
      )

      // When
      const aroundMe = wrapper.findWhere(node => node.text() === 'Partout').first()

      // Then
      expect(aroundMe).toHaveLength(1)
    })
  })
})
