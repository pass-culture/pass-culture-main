import { mount, shallow } from 'enzyme'
import React from 'react'
import { Route, Router } from 'react-router'
import { Criteria } from '../Criteria/Criteria'
import SearchResults from '../Result/SearchResults'
import SearchAlgolia from '../SearchAlgolia'
import { Home } from '../Home/Home'
import { createBrowserHistory } from 'history'

describe('components | SearchAlgolia', () => {
  let props
  beforeEach(() => {
    props = {
      geolocation: {
        latitude: 32,
        longitude: 45,
      },
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
    }
  })

  describe('routing', () => {
    it('should render home page when path is exactly /recherche-offres', () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // when
      const routes = wrapper.find(Route)

      // then
      expect(routes.at(0).prop('path')).toBe('/recherche-offres(/menu)?')
      expect(routes.at(0).prop('exact')).toBe(true)
      const home = routes.at(0).find(Home)
      expect(home).toHaveLength(1)
      expect(home.prop('categoryCriterion')).toStrictEqual({
        filters: [],
        icon: 'ico-gem-stone',
        label: 'Toutes les catégories'
      })
      expect(home.prop('geolocationCriterion')).toStrictEqual({
        isSearchAroundMe: false,
        params: { icon: 'ico-globe', label: 'Partout', requiresGeolocation: false }
      })
      expect(home.prop('history')).toStrictEqual(props.history)
      expect(home.prop('sortCriterion')).toStrictEqual({
        icon: 'ico-random',
        index: '',
        label: 'Au hasard',
        requiresGeolocation: false
      })
    })

    it('should render search results page when path is /recherche-offres/resultats', () => {
      // given
      props.history.location.pathname = 'recherche-offres/resultats'
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // when
      const routes = wrapper.find(Route)

      // then
      const resultatsRoute = routes.at(1)
      expect(resultatsRoute.prop('path')).toBe('/recherche-offres/resultats')
      const searchResultsComponent = resultatsRoute.find(SearchResults)
      expect(searchResultsComponent.prop('categoriesFilter')).toStrictEqual([])
      expect(searchResultsComponent.prop('geolocation')).toStrictEqual(props.geolocation)
      expect(searchResultsComponent.prop('isSearchAroundMe')).toStrictEqual(props.isGeolocationEnabled)
      expect(searchResultsComponent.prop('history')).toStrictEqual(props.history)
      expect(searchResultsComponent.prop('match')).toStrictEqual(props.match)
      expect(searchResultsComponent.prop('query')).toStrictEqual(props.query)
      expect(searchResultsComponent.prop('redirectToSearchMainPage')).toStrictEqual(props.redirectToSearchMainPage)
      expect(searchResultsComponent.prop('search')).toStrictEqual(props.history.location.search)
      expect(searchResultsComponent.prop('sortingIndexSuffix')).toStrictEqual('')
    })

    it('should render geolocation criteria page when path is /recherche-offres/criteres-localisation', () => {
      // given
      props.history.location.pathname = 'recherche-offres/criteres-localisation'
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // when
      const routes = wrapper.find(Route)

      // then
      const critereLocalisationRoute = routes.at(2)
      expect(critereLocalisationRoute.prop('path')).toBe('/recherche-offres/criteres-localisation')
      const searchCriteriaLocation = critereLocalisationRoute.find(Criteria)
      expect(searchCriteriaLocation.prop('activeCriterionLabel')).toStrictEqual('Partout')
      expect(searchCriteriaLocation.prop('criteria')).toStrictEqual(expect.any(Object))
      expect(searchCriteriaLocation.prop('history')).toStrictEqual(props.history)
      expect(searchCriteriaLocation.prop('match')).toStrictEqual(props.match)
      expect(searchCriteriaLocation.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
      expect(searchCriteriaLocation.prop('title')).toStrictEqual('Localisation')
    })

    it('should render category criteria page when path is /recherche-offres/criteres-categorie', () => {
      // given
      props.history.location.pathname = '/recherche-offres/criteres-categorie'
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // when
      const routes = wrapper.find(Route)

      // then
      const critereCategorieRoute = routes.at(3)
      expect(critereCategorieRoute.prop('path')).toBe('/recherche-offres/criteres-categorie')
      const searchCriteriaCategory = critereCategorieRoute.find(Criteria)
      expect(searchCriteriaCategory.prop('activeCriterionLabel')).toStrictEqual('Toutes les catégories')
      expect(searchCriteriaCategory.prop('criteria')).toStrictEqual(expect.any(Object))
      expect(searchCriteriaCategory.prop('history')).toStrictEqual(props.history)
      expect(searchCriteriaCategory.prop('match')).toStrictEqual(props.match)
      expect(searchCriteriaCategory.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
      expect(searchCriteriaCategory.prop('title')).toStrictEqual('Catégories')
    })

    it('should render sorting criteria page when path is /recherche-offres/criteres-tri', () => {
      // given
      props.history.location.pathname = '/recherche-offres/criteres-tri'
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // when
      const routes = wrapper.find(Route)

      // then
      const sortingCriteriaRoute = routes.at(4)
      expect(sortingCriteriaRoute.prop('path')).toBe('/recherche-offres/criteres-tri')
      const sortingCriteria = sortingCriteriaRoute.find(Criteria)
      expect(sortingCriteria.prop('activeCriterionLabel')).toStrictEqual('Au hasard')
      expect(sortingCriteria.prop('criteria')).toStrictEqual(expect.any(Object))
      expect(sortingCriteria.prop('history')).toStrictEqual(props.history)
      expect(sortingCriteria.prop('match')).toStrictEqual(props.match)
      expect(sortingCriteria.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
      expect(sortingCriteria.prop('title')).toStrictEqual('Trier par')
    })
  })

  describe('when rendering', () => {
    it('should select "Autour de moi" if geolocation is enabled', () => {
      // given
      props.isGeolocationEnabled = true
      props.history.location.pathname = '/recherche-offres'
      const wrapper = mount(
        <Router history={props.history}>
          <SearchAlgolia {...props} />
        </Router>
      )

      // when
      const aroundMe = wrapper.findWhere(node => node.text() === 'Autour de moi').first()

      // then
      expect(aroundMe).toHaveLength(1)
    })

    it('should select "Partout" if geolocation is disabled', () => {
      // given
      props.isGeolocationEnabled = false
      props.history.location.pathname = '/recherche-offres'
      const wrapper = mount(
        <Router history={props.history}>
          <SearchAlgolia {...props} />
        </Router>
      )

      // when
      const aroundMe = wrapper.findWhere(node => node.text() === 'Partout').first()

      // then
      expect(aroundMe).toHaveLength(1)
    })

    it('should select "Toutes les catégories" by default', () => {
      // given
      props.history.location.pathname = '/recherche-offres/criteres-categorie'
      const wrapper = mount(
        <Router history={props.history}>
          <SearchAlgolia {...props} />
        </Router>
      )

      // when
      const aroundMe = wrapper.findWhere(node => node.text() === 'Toutes les catégories').first()

      // then
      expect(aroundMe).toHaveLength(1)
    })
  })
})
