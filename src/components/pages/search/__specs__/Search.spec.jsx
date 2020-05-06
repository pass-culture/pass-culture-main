import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Route, Router } from 'react-router'
import { CATEGORY_CRITERIA } from '../Criteria/criteriaEnums'
import { CriteriaCategory } from '../CriteriaCategory/CriteriaCategory'
import CriteriaLocation from '../CriteriaLocation/CriteriaLocation'
import { CriteriaSort } from '../CriteriaSort/CriteriaSort'
import { Home } from '../Home/Home'
import Results from '../Results/Results'
import Search from '../Search'

describe('components | Search', () => {
  let props

  beforeEach(() => {
    props = {
      geolocation: {
        latitude: 32,
        longitude: 45,
      },
      history: createBrowserHistory(),
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

  describe('render', () => {
    it('should define a resize event to prevent page from resizing when Android keyboard is displayed', () => {
      // Given
      const metaTag = document.createElement('meta')
      jest
        .spyOn(document, 'querySelector')
        .mockReturnValueOnce({ offsetHeight: 123 })
        .mockReturnValue(metaTag)
      shallow(<Search {...props} />)

      // When
      window.onresize()

      // Then
      expect(document.querySelector().content).toMatch(
        'height=123px, width=device-width, initial-scale=1, user-scalable=no, shrink-to-fit=no'
      )
    })

    it('should reset the resize event and meta tag when unmounting', () => {
      // Given
      const metaTag = document.createElement('meta')
      jest.spyOn(document, 'querySelector').mockReturnValue(metaTag)
      const wrapper = shallow(<Search {...props} />)

      // When
      wrapper.unmount()

      // Then
      expect(window.onresize).toBeNull()
      expect(document.querySelector().content).toBe(
        'width=device-width, initial-scale=1, user-scalable=no, shrink-to-fit=no'
      )
    })

    it('should select "Partout" by default', () => {
      // given
      props.history.location.pathname = '/recherche'
      const wrapper = mount(
        <Router history={props.history}>
          <Search {...props} />
        </Router>
      )

      // when
      const geolocationCriterion = wrapper.find({ children: 'Partout' })

      // then
      expect(geolocationCriterion).toHaveLength(1)
    })

    it('should select "Toutes les catégories" by default', () => {
      // given
      props.history.location.pathname = '/recherche/criteres-categorie'
      const wrapper = mount(
        <Router history={props.history}>
          <Search {...props} />
        </Router>
      )

      // when
      const categoryCriterion = wrapper.find({ children: 'Toutes les catégories' })

      // then
      expect(categoryCriterion).toHaveLength(1)
    })

    it('should select "Pertinence" by default', () => {
      // given
      props.history.location.pathname = '/recherche/criteres-tri'
      const wrapper = mount(
        <Router history={props.history}>
          <Search {...props} />
        </Router>
      )

      // when
      const sortCriterion = wrapper.find({ children: 'Pertinence' })

      // then
      expect(sortCriterion).toHaveLength(1)
    })
  })

  describe('routing', () => {
    describe('home page', () => {
      it('should render search home page when path is exactly /recherche', () => {
        // when
        const wrapper = shallow(<Search {...props} />)

        // then
        const routes = wrapper.find(Route)
        expect(routes.at(0).prop('path')).toBe('/recherche(/menu)?')
        expect(routes.at(0).prop('exact')).toBe(true)
        const home = wrapper.find(Home)
        expect(home).toHaveLength(1)
        expect(home.prop('categoryCriterion')).toStrictEqual({
          facetFilter: '',
          icon: 'ico-all',
          label: 'Toutes les catégories'
        })
        expect(home.prop('geolocationCriterion')).toStrictEqual({
          params: {
            icon: 'ico-everywhere',
            label: 'Partout',
            requiresGeolocation: false
          },
          place: null,
          searchAround: {
            'everywhere': true,
            'place': false,
            'user': false
          },
          userGeolocation: {
            latitude: 32,
            longitude: 45
          }
        })
        expect(home.prop('history')).toStrictEqual(props.history)
        expect(home.prop('sortCriterion')).toStrictEqual({
          icon: 'ico-relevance',
          index: '',
          label: 'Pertinence',
          requiresGeolocation: false,
        })
      })
    })

    describe('results page', () => {
      it('should render search results page when path is /recherche/resultats', () => {
        // given
        props.history.location.pathname = 'recherche/resultats'
        const wrapper = shallow(<Search {...props} />)

        // when
        const routes = wrapper.find(Route)

        // then
        const resultatsRoute = routes.at(1)
        expect(resultatsRoute.prop('path')).toBe('/recherche/resultats')
        const searchResultsComponent = resultatsRoute.find(Results)
        expect(searchResultsComponent.prop('criteria')).toStrictEqual({
          categories: [],
          searchAround: { 'everywhere': true, 'place': false, 'user': false },
          sortBy: '',
        })
        expect(searchResultsComponent.prop('history')).toStrictEqual(props.history)
        expect(searchResultsComponent.prop('match')).toStrictEqual(props.match)
        expect(searchResultsComponent.prop('query')).toStrictEqual(props.query)
        expect(searchResultsComponent.prop('redirectToSearchMainPage')).toStrictEqual(props.redirectToSearchMainPage)
        expect(searchResultsComponent.prop('search')).toStrictEqual(props.history.location.search)
        expect(searchResultsComponent.prop('userGeolocation')).toStrictEqual(props.geolocation)
      })

      it('should render search results page with given category when path is /recherche/resultats', () => {
        // given
        props.history.location.pathname = 'recherche/resultats'
        const wrapper = shallow(<Search {...props} />)
        wrapper.setState({ categoryCriterion: CATEGORY_CRITERIA.CINEMA })

        // when
        const routes = wrapper.find(Route)

        // then
        const resultatsRoute = routes.at(1)
        expect(resultatsRoute.prop('path')).toBe('/recherche/resultats')
        const searchResultsComponent = resultatsRoute.find(Results)
        expect(searchResultsComponent.prop('criteria')).toStrictEqual({
          categories: ['CINEMA'],
          searchAround: { 'everywhere': true, 'place': false, 'user': false },
          sortBy: '',
        })
      })
    })

    describe('geolocation criteria page', () => {
      it('should render geolocation criteria page when path is /recherche/criteres-localisation', () => {
        // given
        props.history.location.pathname = '/recherche/criteres-localisation'
        const wrapper = shallow(<Search {...props} />)

        // when
        const routes = wrapper.find(Route)

        // then
        const criteriaLocationRoute = routes.at(2)
        expect(criteriaLocationRoute.prop('path')).toBe('/recherche/criteres-localisation')
        const searchCriteriaLocation = criteriaLocationRoute.find(CriteriaLocation)
        expect(searchCriteriaLocation.prop('activeCriterionLabel')).toStrictEqual('Partout')
        expect(searchCriteriaLocation.prop('backTo')).toStrictEqual('/recherche')
        expect(searchCriteriaLocation.prop('criteria')).toStrictEqual(expect.any(Object))
        expect(searchCriteriaLocation.prop('geolocation')).toStrictEqual(props.geolocation)
        expect(searchCriteriaLocation.prop('history')).toStrictEqual(props.history)
        expect(searchCriteriaLocation.prop('match')).toStrictEqual(props.match)
        expect(searchCriteriaLocation.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
        expect(searchCriteriaLocation.prop('onPlaceSelection')).toStrictEqual(expect.any(Function))
        expect(searchCriteriaLocation.prop('place')).toBeNull()
        expect(searchCriteriaLocation.prop('title')).toStrictEqual('Localisation')
      })

      it('should redirect to main page when clicking on "Partout" option', () => {
        // given
        props.history.push('/recherche/criteres-localisation')
        const wrapper = mount(
          <Router history={props.history}>
            <Search {...props} />
          </Router>
        )
        const everywhereButton = wrapper.find({ children: 'Partout' })

        // when
        everywhereButton.simulate('click')

        // then
        expect(props.redirectToSearchMainPage).toHaveBeenCalledTimes(1)
      })
    })

    describe('category criteria page', () => {
      it('should render category criteria page when path is /recherche/criteres-categorie', () => {
        // given
        props.history.location.pathname = '/recherche/criteres-categorie'
        const wrapper = shallow(<Search {...props} />)

        // when
        const routes = wrapper.find(Route)

        // then
        const criteriaCategoryRoute = routes.at(3)
        expect(criteriaCategoryRoute.prop('path')).toBe('/recherche/criteres-categorie')
        const criteriaCategory = criteriaCategoryRoute.find(CriteriaCategory)
        expect(criteriaCategory.prop('activeCriterionLabel')).toStrictEqual('Toutes les catégories')
        expect(criteriaCategory.prop('criteria')).toStrictEqual(expect.any(Object))
        expect(criteriaCategory.prop('history')).toStrictEqual(props.history)
        expect(criteriaCategory.prop('match')).toStrictEqual(props.match)
        expect(criteriaCategory.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
        expect(criteriaCategory.prop('title')).toStrictEqual('Catégories')
      })
    })

    describe('sort criteria page', () => {
      it('should render sorting criteria page when path is /recherche/criteres-tri', () => {
        // given
        props.history.location.pathname = '/recherche/criteres-tri'
        const wrapper = shallow(<Search {...props} />)

        // when
        const routes = wrapper.find(Route)

        // then
        const criteriaSortRoute = routes.at(4)
        expect(criteriaSortRoute.prop('path')).toBe('/recherche/criteres-tri')
        const criteriaSort = criteriaSortRoute.find(CriteriaSort)
        expect(criteriaSort.prop('activeCriterionLabel')).toStrictEqual('Pertinence')
        expect(criteriaSort.prop('criteria')).toStrictEqual(expect.any(Object))
        expect(criteriaSort.prop('geolocation')).toStrictEqual(props.geolocation)
        expect(criteriaSort.prop('history')).toStrictEqual(props.history)
        expect(criteriaSort.prop('match')).toStrictEqual(props.match)
        expect(criteriaSort.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
        expect(criteriaSort.prop('title')).toStrictEqual('Trier par')
      })
    })
  })
})
