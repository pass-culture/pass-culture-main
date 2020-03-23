import { mount, shallow } from 'enzyme'
import React from 'react'
import { Filters } from '../Filters'
import { Criteria } from '../../Criteria/Criteria'
import { GEOLOCATION_CRITERIA } from '../../Criteria/criteriaEnums'
import HeaderContainer from '../../../../layout/Header/HeaderContainer'
import { Router } from 'react-router'
import { createBrowserHistory } from 'history'
import { fetchAlgolia } from '../../../../../vendor/algolia/algolia'
import FilterCheckbox from '../FilterCheckbox/FilterCheckbox'

jest.mock('../../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn(),
}))
describe('components | Filters', () => {
  let props

  beforeEach(() => {
    props = {
      geolocation: {
        latitude: 40,
        longitude: 41
      },
      history: {
        location: {
          pathname: '',
          search: ''
        },
        listen: jest.fn(),
        push: jest.fn(),
        replace: jest.fn()
      },
      initialFilters: {
        categories: ['Musée', 'Cinéma'],
        isSearchAroundMe: false,
        offerTypes: {
          isDigital: false
        },
        sortCriteria: '_by_price'
      },
      isGeolocationEnabled: false,
      isUserAllowedToSelectCriterion: jest.fn(),
      match: {
        params: {}
      },
      offers: {
        hits: [],
        nbHits: 0,
        nbPages: 0
      },
      query: {
        parse: jest.fn()
      },
      redirectToSearchFiltersPage: jest.fn(),
      showFailModal: jest.fn(),
      updateFilteredOffers: jest.fn(),
      updateFilters: jest.fn()
    }
  })

  describe('render', () => {
    describe('localisation filter page', () => {
      it('should render localisation filter page when on route /recherche-offres/filtres/localisation', () => {
        // given
        props.history.location.pathname = '/recherche-offres/resultats/filtres/localisation'
        props.history.location.search = '?mots-cles=librairie'

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const criteria = wrapper.find(Criteria)
        expect(criteria).toHaveLength(1)
        expect(criteria.prop('backTo')).toStrictEqual('/recherche-offres/resultats/filtres?mots-cles=librairie')
        expect(criteria.prop('criteria')).toStrictEqual(GEOLOCATION_CRITERIA)
        expect(criteria.prop('history')).toStrictEqual(props.history)
        expect(criteria.prop('match')).toStrictEqual(props.match)
        expect(criteria.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
        expect(criteria.prop('title')).toStrictEqual('Localisation')
      })

      it('should render a Criteria component with a "Partout" criterion when not searching around me', () => {
        // given
        props.history.location.pathname = '/recherche-offres/resultats/filtres/localisation'
        props.initialFilters.isSearchAroundMe = false

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const criteria = wrapper.find(Criteria)
        expect(criteria.prop('activeCriterionLabel')).toStrictEqual('Partout')
      })

      describe('when searching everywhere', () => {
        it('should trigger search to Algolia and redirect to filters page when clicking on "Partout" criterion', () => {
          // given
          props.history = createBrowserHistory()
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
          props.history.location.pathname = '/recherche-offres/resultats/filtres/localisation'
          props.isUserAllowedToSelectCriterion.mockReturnValue(true)
          props.query.parse.mockReturnValue({
            'autour-de-moi': 'non',
            'categories': 'Musée;Cinéma',
            'mots-cles': 'librairie',
            'tri': '_by_price'
          })
          fetchAlgolia.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [],
                nbHits: 0,
                page: 0,
              })
            })
          )
          const wrapper = mount(
            <Router history={props.history}>
              <Filters {...props} />
            </Router>
          )
          const everywhereButton = wrapper.find(Criteria).find('button').at(0)

          // when
          everywhereButton.simulate('click')

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            categories: ['Musée', 'Cinéma'],
            geolocationCoordinates: null,
            indexSuffix: '_by_price',
            keywords: 'librairie',
            offerTypes: { isDigital: false },
            page: 0,
          })
          expect(props.redirectToSearchFiltersPage).toHaveBeenCalledWith()
          expect(props.history.replace).toHaveBeenCalledWith({ search: '?mots-cles=librairie&autour-de-moi=non&tri=_by_price&categories=Musée;Cinéma' })
        })
      })

      describe('when searching around me', () => {
        it('should trigger search to Algolia and redirect to filters page when clicking on "Autour de moi" criterion', () => {
          // given
          props.history = createBrowserHistory()
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
          props.history.location.pathname = '/recherche-offres/resultats/filtres/localisation'
          props.initialFilters = {
            categories: ['Musée'],
            isSearchAroundMe: false,
            offerTypes: { isDigital: false },
            sortCriteria: '_by_price'
          }
          props.isUserAllowedToSelectCriterion.mockReturnValue(true)
          props.query.parse.mockReturnValue({
            'autour-de-moi': 'oui',
            'categories': 'Musée',
            'mots-cles': 'librairie',
            'tri': '_by_price'
          })
          fetchAlgolia.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [],
                nbHits: 0,
                page: 0,
              })
            })
          )
          const wrapper = mount(
            <Router history={props.history}>
              <Filters {...props} />
            </Router>
          )
          const aroundMeButton = wrapper.find(Criteria).find('button').at(1)

          // when
          aroundMeButton.simulate('click')

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            categories: ['Musée'],
            geolocationCoordinates: { latitude: 40, longitude: 41 },
            indexSuffix: '_by_price',
            keywords: 'librairie',
            offerTypes: { isDigital: false },
            page: 0,
          })
          expect(props.redirectToSearchFiltersPage).toHaveBeenCalledWith()
          expect(props.history.replace).toHaveBeenCalledWith({ search: '?mots-cles=librairie&autour-de-moi=oui&tri=_by_price&categories=Musée' })
        })
      })
    })

    describe('filters page', () => {
      it('should render a Header component with the right props', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.history.location.search = '?mots-cles=librairie'

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const header = wrapper.find(HeaderContainer)
        expect(header).toHaveLength(1)
        expect(header.prop('backTo')).toStrictEqual('/recherche-offres/resultats?mots-cles=librairie')
        expect(header.prop('closeTo')).toBeNull()
        expect(header.prop('reset')).toStrictEqual(expect.any(Function))
        expect(header.prop('title')).toStrictEqual('Filtrer')
      })

      it('should display the number of results on the display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.offers.nbHits = 10

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const numberOfResults = wrapper.findWhere(node => node.text() === 'Afficher les 10 résultats').first()
        expect(numberOfResults).toHaveLength(1)
      })

      it('should display "999+" on the display results button when number of results exceeds 999', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.offers.nbHits = 1000

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const numberOfResults = wrapper.findWhere(node => node.text() === 'Afficher les 999+ résultats').first()
        expect(numberOfResults).toHaveLength(1)
      })

      it('should filter offers when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.offers.nbHits = 1000
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.updateFilteredOffers).toHaveBeenCalledWith({ hits: [], nbHits: 1000, nbPages: 0 })
      })

      it('should redirect to results page with query param when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.history.location.search = '?mots-cles=librairie'
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.history.push).toHaveBeenCalledWith('/recherche-offres/resultats?mots-cles=librairie')
      })

      it('should redirect to results page with no query param when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.history.push).toHaveBeenCalledWith('/recherche-offres/resultats')
      })

      it('should update filters when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.updateFilters).toHaveBeenCalledWith({
          categories: ['Musée', 'Cinéma'],
          isSearchAroundMe: false,
          offerTypes: { isDigital: false },
          sortCriteria: '_by_price'
        })
      })

      describe('geolocation filter', () => {
        it('should display a "Localisation" title for geolocation filter', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.findWhere(node => node.text() === 'Localisation').first()
          expect(title).toHaveLength(1)
        })

        it('should display a "Partout" for geolocation filter when initial filter is "Partout"', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.isSearchAroundMe = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const button = wrapper.findWhere(node => node.text() === 'Partout').first()
          expect(button).toHaveLength(1)
        })

        it('should display a "Autour de moi" for geolocation filter when initial filter is "Autour de moi"', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.isSearchAroundMe = true

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const button = wrapper.findWhere(node => node.text() === 'Autour de moi').first()
          expect(button).toHaveLength(1)
        })

        it('should redirect to localisation filter page with given query params when clicking on geolocation filter button', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.history.location.search = '?mots-cles=librairie'
          props.initialFilters.isSearchAroundMe = true
          const wrapper = shallow(<Filters {...props} />)
          const button = wrapper.findWhere(node => node.text() === 'Autour de moi').first()

          // when
          button.simulate('click')

          // then
          expect(props.history.push).toHaveBeenCalledWith('/recherche-offres/resultats/filtres/localisation?mots-cles=librairie')
        })

        it('should redirect to localisation filter page with no query params when clicking on geolocation filter button', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.isSearchAroundMe = true
          const wrapper = shallow(<Filters {...props} />)
          const button = wrapper.findWhere(node => node.text() === 'Autour de moi').first()

          // when
          button.simulate('click')

          // then
          expect(props.history.push).toHaveBeenCalledWith('/recherche-offres/resultats/filtres/localisation')
        })
      })

      describe('reset', () => {
        describe('when single categorie', () => {
          it('should reset filters and trigger search to Algolia with given category', () => {
            // given
            props.history = createBrowserHistory()
            jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
            props.history.location.pathname = '/recherche-offres/resultats/filtres'
            props.initialFilters = {
              categories: ['Musée'],
              isSearchAroundMe: true,
              offerTypes: { isDigital: false },
              sortCriteria: '_by_price'
            }
            props.query.parse.mockReturnValue({
              'mots-cles': 'librairie'
            })
            fetchAlgolia.mockReturnValue(
              new Promise(resolve => {
                resolve({
                  hits: [],
                  nbHits: 0,
                  page: 0,
                })
              })
            )
            const wrapper = mount(
              <Router history={props.history}>
                <Filters {...props} />
              </Router>
            )
            const resetButton = wrapper.find(HeaderContainer).find('.reset-button').first()

            // when
            resetButton.simulate('click')

            // then
            expect(fetchAlgolia).toHaveBeenCalledWith({
              categories: ['Musée'],
              geolocationCoordinates: { latitude: 40, longitude: 41 },
              indexSuffix: '_by_price',
              keywords: 'librairie',
              offerTypes: { isDigital: false },
              page: 0
            })
          })
        })
        describe('when multiple categories', () => {
          it('should reset filters and trigger search to Algolia with given categories', () => {
            // given
            props.history = createBrowserHistory()
            jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
            props.history.location.pathname = '/recherche-offres/resultats/filtres'
            props.initialFilters = {
              categories: ['Musée', 'Cinéma'],
              isSearchAroundMe: true,
              offerTypes: { isDigital: true },
              sortCriteria: '_by_price'
            }
            props.query.parse.mockReturnValue({
              'mots-cles': 'librairie'
            })
            fetchAlgolia.mockReturnValue(
              new Promise(resolve => {
                resolve({
                  hits: [],
                  nbHits: 0,
                  page: 0,
                })
              })
            )
            const wrapper = mount(
              <Router history={props.history}>
                <Filters {...props} />
              </Router>
            )
            const resetButton = wrapper.find(HeaderContainer).find('.reset-button').first()

            // when
            resetButton.simulate('click')

            // then
            expect(fetchAlgolia).toHaveBeenCalledWith({
              categories: ['Musée', 'Cinéma'],
              geolocationCoordinates: { latitude: 40, longitude: 41 },
              indexSuffix: '_by_price',
              keywords: 'librairie',
              offerTypes: { isDigital: false },
              page: 0,
            })
          })
        })
      })

      describe('offer type', () => {
        it('should display a "Type d\'offres" title for offer types filter', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.findWhere(node => node.text() === 'Type d\'offres').first()
          expect(title).toHaveLength(1)
        })

        it('should render a FilterCheckbox component unchecked when offer filter is not checked', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerTypes.isDigital = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const filterCheckbox = wrapper.find(FilterCheckbox)
          expect(filterCheckbox).toHaveLength(1)
          expect(filterCheckbox.prop('checked')).toBe(false)
          expect(filterCheckbox.prop('className')).toBe('fc-label')
          expect(filterCheckbox.prop('id')).toBe('isDigital')
          expect(filterCheckbox.prop('label')).toBe('Offres numériques')
          expect(filterCheckbox.prop('name')).toBe('isDigital')
          expect(filterCheckbox.prop('onChange')).toStrictEqual(expect.any(Function))
        })

        it('should render a FilterCheckbox component checked when offer filter is checked', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerTypes.isDigital = true

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const filterCheckbox = wrapper.find(FilterCheckbox)
          expect(filterCheckbox).toHaveLength(1)
          expect(filterCheckbox.prop('checked')).toBe(true)
          expect(filterCheckbox.prop('className')).toBe('fc-label-checked')
        })

        it('should display the number of offer types selected when filter is checked', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerTypes.isDigital = true

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper.findWhere(node => node.text() === '(1)').first()
          expect(numberOfOfferTypesSelected).toHaveLength(1)
        })

        it('should not display the number of offer types selected when filter is not checked', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerTypes.isDigital = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper.findWhere(node => node.text() === '(1)').first()
          expect(numberOfOfferTypesSelected).toHaveLength(0)
        })
      })
    })
  })
})
