import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Route, Router } from 'react-router'
import { Criteria } from '../Criteria/Criteria'
import SearchResults from '../Result/SearchResults'
import SearchAlgolia from '../SearchAlgolia'

describe('components | SearchAlgolia', () => {
  let props
  beforeEach(() => {
    props = {
      history: createBrowserHistory(),
      isGeolocationEnabled: false,
      isUserAllowedToSelectCriterion: jest.fn(),
      match: {
        params: {},
      },
      query: {
        clear: jest.fn(),
        change: jest.fn(),
        parse: jest.fn(),
      },
      redirectToSearchMainPage: jest.fn(),
      geolocation: {
        latitude: 32,
        longitude: 45,
      },
    }
  })

  describe('routing', () => {
    it('should render Home page when path is exactly /recherche-offres', () => {
      // Given
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // When
      const routes = wrapper.find(Route)

      // Then
      expect(routes.at(0).prop('path')).toBe('/recherche-offres(/menu)?')
      expect(
        routes
          .at(0)
          .children()
          .type().name
      ).toStrictEqual('Home')
      expect(routes.at(0).prop('exact')).toBeDefined()
    })

    it('should render search results page when path is /recherche-offres/resultats', () => {
      // Given
      props.history.location.pathname = 'recherche-offres/resultats'
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // When
      const routes = wrapper.find(Route)

      // Then
      const resultatsRoute = routes.at(1)
      expect(resultatsRoute.prop('path')).toBe('/recherche-offres/resultats')
      const searchResultsComponent = resultatsRoute.find(SearchResults)
      expect(searchResultsComponent.prop('categoriesFilter')).toStrictEqual([])
      expect(searchResultsComponent.prop('geolocation')).toStrictEqual(props.geolocation)
      expect(searchResultsComponent.prop('isSearchAroundMe')).toStrictEqual(
        props.isGeolocationEnabled
      )
      expect(searchResultsComponent.prop('history')).toStrictEqual(props.history.location.search)
      expect(searchResultsComponent.prop('match')).toStrictEqual(props.match)
      expect(searchResultsComponent.prop('query')).toStrictEqual(props.query)
      expect(searchResultsComponent.prop('redirectToSearchMainPage')).toStrictEqual(
        props.redirectToSearchMainPage
      )
    })

    it('should render geolocation criteria page when path is /recherche-offres/criteres-localisation', () => {
      // Given
      props.history.location.pathname = 'recherche-offres/criteres-localisation'
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // When
      const routes = wrapper.find(Route)

      // Then
      const critereLocalisationRoute = routes.at(2)
      expect(critereLocalisationRoute.prop('path')).toBe('/recherche-offres/criteres-localisation')

      const searchCriteriaLocation = critereLocalisationRoute.find(Criteria)
      expect(searchCriteriaLocation.prop('activeCriterionLabel')).toStrictEqual('Partout')
      expect(searchCriteriaLocation.prop('criteria')).toStrictEqual(expect.any(Object))
      expect(searchCriteriaLocation.prop('history')).toStrictEqual(props.history)
      expect(searchCriteriaLocation.prop('match')).toStrictEqual(props.match)
      expect(searchCriteriaLocation.prop('onCriterionSelection')).toStrictEqual(
        expect.any(Function)
      )
      expect(searchCriteriaLocation.prop('title')).toStrictEqual('Localisation')
    })

    it('should render category criteria page when path is /recherche-offres/criteres-categorie', () => {
      // Given
      props.history.location.pathname = '/recherche-offres/criteres-categorie'
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // When
      const routes = wrapper.find(Route)

      // Then
      const critereCategorieRoute = routes.at(3)
      expect(critereCategorieRoute.prop('path')).toBe('/recherche-offres/criteres-categorie')

      const searchCriteriaCategory = critereCategorieRoute.find(Criteria)
      expect(searchCriteriaCategory.prop('activeCriterionLabel')).toStrictEqual(
        'Toutes les catégories'
      )
      expect(searchCriteriaCategory.prop('criteria')).toStrictEqual(expect.any(Object))
      expect(searchCriteriaCategory.prop('history')).toStrictEqual(props.history)
      expect(searchCriteriaCategory.prop('match')).toStrictEqual(props.match)
      expect(searchCriteriaCategory.prop('onCriterionSelection')).toStrictEqual(
        expect.any(Function)
      )
      expect(searchCriteriaCategory.prop('title')).toStrictEqual('Catégories')
    })
  })

  describe('when rendering', () => {
    it('should select "Autour de moi" if geolocation is enabled', () => {
      // Given
      props.isGeolocationEnabled = true
      props.history.location.pathname = '/recherche-offres'
      const wrapper = mount(
        <Router history={props.history}>
          <SearchAlgolia {...props} />
        </Router>
      )

      // When
      const aroundMe = wrapper.findWhere(node => node.text() === 'Autour de moi').first()

      // Then
      expect(aroundMe).toHaveLength(1)
    })

    it('should select "Partout" if geolocation is disabled', () => {
      // Given
      props.isGeolocationEnabled = false
      props.history.location.pathname = '/recherche-offres'
      const wrapper = mount(
        <Router history={props.history}>
          <SearchAlgolia {...props} />
        </Router>
      )

      // When
      const aroundMe = wrapper.findWhere(node => node.text() === 'Partout').first()

      // Then
      expect(aroundMe).toHaveLength(1)
    })

    it('should select "Toutes les catégories" by default', () => {
      // Given
      props.history.location.pathname = '/recherche-offres/criteres-categorie'
      const wrapper = mount(
        <Router history={props.history}>
          <SearchAlgolia {...props} />
        </Router>
      )

      // When
      const aroundMe = wrapper.findWhere(node => node.text() === 'Toutes les catégories').first()

      // Then
      expect(aroundMe).toHaveLength(1)
    })
  })
})
