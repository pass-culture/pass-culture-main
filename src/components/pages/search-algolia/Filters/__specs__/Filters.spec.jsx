import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import Slider, { Range } from 'rc-slider'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'
import configureStore from 'redux-mock-store'

import { fetchAlgolia } from '../../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../../layout/Header/HeaderContainer'
import { GEOLOCATION_CRITERIA } from '../../Criteria/criteriaEnums'
import { Filters } from '../Filters'
import FilterToggle from '../FilterToggle/FilterToggle'
import { CriteriaLocation } from '../../CriteriaLocation/CriteriaLocation'
import FilterCheckbox from '../FilterCheckbox/FilterCheckbox'
import { Criteria } from '../../Criteria/Criteria'

jest.mock('../../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn(),
}))
describe('components | Filters', () => {
  const actualDate = global.Date
  const now = new Date(2020, 3, 14)
  const store = configureStore([])()
  let props

  beforeEach(() => {
    props = {
      geolocation: {
        latitude: 40,
        longitude: 41,
      },
      history: {
        location: {
          pathname: '',
          search: '',
        },
        listen: jest.fn(),
        push: jest.fn(),
        replace: jest.fn(),
      },
      initialFilters: {
        aroundRadius: 100,
        date: {
          option: 'today',
          selectedDate: null,
        },
        offerIsFilteredByDate: false,
        isSearchAroundMe: false,
        offerCategories: ['VISITE', 'CINEMA'],
        offerIsDuo: false,
        offerIsFree: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        priceRange: [0, 500],
        sortBy: '_by_price',
      },
      isGeolocationEnabled: false,
      match: {
        params: {},
      },
      offers: {
        hits: [],
        nbHits: 0,
        nbPages: 0,
      },
      query: {
        parse: jest.fn(),
      },
      showFailModal: jest.fn(),
      updateFilters: jest.fn(),
      updateFilteredOffers: jest.fn(),
      updateNumberOfActiveFilters: jest.fn(),
    }
    props.query.parse.mockReturnValue({
      'mots-cles': '',
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
    jest.spyOn(global, 'Date').mockImplementation(() => now)
    global.Date.now = jest.fn(() => now.getTime())
  })

  afterEach(() => {
    global.Date = actualDate
    global.Date.now = actualDate.now
    fetchAlgolia.mockReset()
    jest.resetAllMocks()
  })

  describe('render', () => {
    describe('localisation filter page', () => {
      it('should render localisation filter page when on route /recherche/filtres/localisation', () => {
        // given
        props.history.location.pathname = '/recherche/resultats/filtres/localisation'
        props.history.location.search = '?mots-cles=librairie'

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const criteria = wrapper.find(CriteriaLocation)
        expect(criteria).toHaveLength(1)
        expect(criteria.prop('backTo')).toStrictEqual(
          '/recherche/resultats/filtres?mots-cles=librairie'
        )
        expect(criteria.prop('criteria')).toStrictEqual(GEOLOCATION_CRITERIA)
        expect(criteria.prop('history')).toStrictEqual(props.history)
        expect(criteria.prop('match')).toStrictEqual(props.match)
        expect(criteria.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
        expect(criteria.prop('title')).toStrictEqual('Localisation')
      })

      it('should render a CriteriaLocation component with a "Partout" criterion when not searching around me', () => {
        // given
        props.history.location.pathname = '/recherche/resultats/filtres/localisation'
        props.initialFilters.isSearchAroundMe = false

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const criteria = wrapper.find(CriteriaLocation)
        expect(criteria.prop('activeCriterionLabel')).toStrictEqual('Partout')
      })

      describe('when clicking on "Partout"', () => {
        it('should trigger search and redirect to filters page when clicking on "Partout" criterion', () => {
          // given
          props.history = createBrowserHistory()
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
          jest.spyOn(props.history, 'push').mockImplementationOnce(() => {})
          props.history.location.pathname = '/recherche/resultats/filtres/localisation'
          props.query.parse.mockReturnValue({
            'autour-de-moi': 'non',
            categories: 'VISITE;CINEMA',
            'mots-cles': 'librairie',
            tri: '_by_price',
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
          const everywhereButton = wrapper
            .find(Criteria)
            .find('button')
            .first()

          // when
          everywhereButton.simulate('click')

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 100,
            date: null,
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            isSearchAroundMe: false,
            keywords: 'librairie',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
          expect(props.history.replace).toHaveBeenCalledWith({
            search: '?mots-cles=librairie&autour-de-moi=non&tri=_by_price&categories=VISITE;CINEMA',
          })
          expect(props.history.push).toHaveBeenCalledWith(
            '/recherche/resultats/filtres?mots-cles=librairie&autour-de-moi=non&tri=_by_price&categories=VISITE;CINEMA'
          )
        })
      })

      describe('when clicking on "Autour de moi"', () => {
        it('should trigger search and redirect to filters page when clicking on "Autour de moi" criterion', () => {
          // given
          props.history = createBrowserHistory()
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
          jest.spyOn(props.history, 'push').mockImplementationOnce(() => {})
          props.history.location.pathname = '/recherche/resultats/filtres/localisation'
          props.initialFilters = {
            ...props.initialFilters,
            aroundRadius: 50,
            isSearchAroundMe: false,
            offerCategories: ['VISITE'],
            offerIsDuo: false,
            offerIsFree: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          }
          props.query.parse.mockReturnValue({
            'autour-de-moi': 'oui',
            categories: 'VISITE',
            'mots-cles': 'librairie',
            tri: '_by_price',
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
          const aroundMeButton = wrapper
            .find(Criteria)
            .find('button')
            .at(1)

          // when
          aroundMeButton.simulate('click')

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 50,
            date: null,
            geolocation: { latitude: 40, longitude: 41 },
            isSearchAroundMe: true,
            keywords: 'librairie',
            offerCategories: ['VISITE'],
            offerIsDuo: false,
            offerIsFree: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
          expect(props.history.replace).toHaveBeenCalledWith({
            search: '?mots-cles=librairie&autour-de-moi=oui&tri=_by_price&categories=VISITE',
          })
          expect(props.history.push).toHaveBeenCalledWith(
            '/recherche/resultats/filtres?mots-cles=librairie&autour-de-moi=oui&tri=_by_price&categories=VISITE'
          )
        })
      })
    })

    describe('filters page', () => {
      it('should render a Header component with the right props', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.history.location.search = '?mots-cles=librairie'

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const header = wrapper.find(HeaderContainer)
        expect(header).toHaveLength(1)
        expect(header.prop('backTo')).toStrictEqual('/recherche/resultats?mots-cles=librairie')
        expect(header.prop('closeTo')).toBeNull()
        expect(header.prop('reset')).toStrictEqual(expect.any(Function))
        expect(header.prop('title')).toStrictEqual('Filtrer')
      })

      it('should display the number of results on the display results button', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.offers.nbHits = 10

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const numberOfResults = wrapper.find({ children: 'Afficher les 10 résultats' })
        expect(numberOfResults).toHaveLength(1)
      })

      it('should display "999+" on the display results button when number of results exceeds 999', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.offers.nbHits = 1000

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const numberOfResults = wrapper.find({ children: 'Afficher les 999+ résultats' })
        expect(numberOfResults).toHaveLength(1)
      })

      it('should filter offers when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.offers.nbHits = 1000
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.updateFilteredOffers).toHaveBeenCalledWith({
          hits: [],
          nbHits: 1000,
          nbPages: 0,
        })
      })

      it('should pass the number of selected filters when clicking on the results button', () => {
        // given
        props.initialFilters.offerCategories = ['VISITE', 'CINEMA']
        props.initialFilters.offerIsFilteredByDate = true
        const history = createBrowserHistory()
        history.push('/recherche/resultats/filtres')
        props.query.parse.mockReturnValue({
          'mots-cles': '',
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
          <Provider store={store}>
            <Router history={history}>
              <Filters {...props} />
            </Router>
          </Provider>
        )
        const resultsButton = wrapper.find('.sf-button')
        const showCategory = wrapper.find('input[name="SPECTACLE"]')
        const digitalOffers = wrapper.find('input[name="isDigital"]')

        const showCategoryEvent = { target: { name: 'SPECTACLE', checked: true } }
        const digitalOffersEvent = { target: { name: 'isDigital', checked: true } }

        showCategory.simulate('change', showCategoryEvent)
        digitalOffers.simulate('change', digitalOffersEvent)

        // when
        resultsButton.props().onClick()

        // then
        expect(props.updateNumberOfActiveFilters).toHaveBeenCalledWith(5)
      })

      it('should redirect to results page with query param when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.history.location.search = '?mots-cles=librairie'
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.history.push).toHaveBeenCalledWith('/recherche/resultats?mots-cles=librairie')
      })

      it('should redirect to results page with no query param when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.history.push).toHaveBeenCalledWith('/recherche/resultats')
      })

      it('should update filters when clicking on display results button', () => {
        // given
        const selectedDate = new Date(2020, 3, 21)
        props.initialFilters.offerIsFilteredByDate = true
        props.initialFilters.date = {
          option: 'currentWeek',
          selectedDate,
        }
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.updateFilters).toHaveBeenCalledWith({
          aroundRadius: 100,
          isSearchAroundMe: false,
          offerIsFilteredByDate: true,
          date: {
            option: 'currentWeek',
            selectedDate,
          },
          offerCategories: ['VISITE', 'CINEMA'],
          offerIsDuo: false,
          offerIsFree: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          priceRange: [0, 500],
          sortBy: '_by_price',
        })
      })

      it('should not allow click on display results button when no results', async () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.query.parse.mockReturnValue({
          'mots-cles': 'librairies',
        })
        props.offers = {
          hits: [{}, {}],
          nbHits: 2,
          page: 0,
        }
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [],
              nbHits: 0,
              page: 0,
            })
          })
        )
        const wrapper = shallow(<Filters {...props} />)
        const offerIsDuoFilter = wrapper
          .find({ children: 'Uniquement les offres duo' })
          .closest('li')
          .find(FilterToggle)
        await offerIsDuoFilter.simulate('change', {
          target: {
            name: 'offerIsDuo',
            checked: true,
          },
        })
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.updateFilters).toHaveBeenCalledTimes(1)
        expect(props.updateFilteredOffers).toHaveBeenCalledTimes(1)
        expect(resultsButton.text()).toStrictEqual('Aucun résultat')
      })

      it('should display a warning message when searching around me', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.initialFilters.isSearchAroundMe = true

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const message = wrapper.find({
          children: 'Seules les offres Sorties et Physiques seront affichées',
        })
        expect(message).toHaveLength(1)
      })

      it('should not display a warning message when not searching around me', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.initialFilters.isSearchAroundMe = false

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const message = wrapper.find({
          children: 'Seules les offres Sorties et Physiques seront affichées',
        })
        expect(message).toHaveLength(0)
      })

      describe('geolocation filter', () => {
        it('should display a "Localisation" title for geolocation filter', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.find({ children: 'Localisation' })
          expect(title).toHaveLength(1)
        })

        it('should display a "Partout" for geolocation filter when initial filter is "Partout"', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.isSearchAroundMe = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const button = wrapper.find({ children: 'Partout' })
          expect(button).toHaveLength(1)
        })

        it('should display a "Autour de moi" for geolocation filter when initial filter is "Autour de moi"', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.isSearchAroundMe = true

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const button = wrapper.find({ children: 'Autour de moi' }).first()
          expect(button).toHaveLength(1)
        })

        it('should redirect to localisation filter page with given query params when clicking on geolocation filter button', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.history.location.search = '?mots-cles=librairie'
          props.initialFilters.isSearchAroundMe = true
          const wrapper = shallow(<Filters {...props} />)
          const button = wrapper.find({ children: 'Autour de moi' })

          // when
          button.simulate('click')

          // then
          expect(props.history.push).toHaveBeenCalledWith(
            '/recherche/resultats/filtres/localisation?mots-cles=librairie'
          )
        })

        it('should redirect to localisation filter page with no query params when clicking on geolocation filter button', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.isSearchAroundMe = true
          const wrapper = shallow(<Filters {...props} />)
          const button = wrapper.find({ children: 'Autour de moi' })

          // when
          button.simulate('click')

          // then
          expect(props.history.push).toHaveBeenCalledWith(
            '/recherche/resultats/filtres/localisation'
          )
        })
      })

      describe('radius filter', () => {
        describe('when geolocation filter is "Partout"', () => {
          it('should not display a "Rayon" title', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.isSearchAroundMe = false

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const title = wrapper.find({ children: 'Rayon' })
            expect(title).toHaveLength(0)
          })

          it('should not display the kilometers radius value', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.aroundRadius = 0
            props.initialFilters.isSearchAroundMe = false

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const kilometersRadius = wrapper.find({ children: '0 km' })
            expect(kilometersRadius).toHaveLength(0)
          })

          it('should not render a Slider component', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.isSearchAroundMe = false

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const slider = wrapper.find(Slider)
            expect(slider).toHaveLength(0)
          })
        })

        describe('when geolocation filter is "Autour de moi"', () => {
          it('should display a "Rayon" title', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.isSearchAroundMe = true

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const title = wrapper.find({ children: 'Rayon' })
            expect(title).toHaveLength(1)
          })

          it('should display the kilometers radius value', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.aroundRadius = 50
            props.initialFilters.isSearchAroundMe = true

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const kilometersRadius = wrapper.find({ children: '50 km' })
            expect(kilometersRadius).toHaveLength(1)
          })

          it('should render a Slider component', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.aroundRadius = 20
            props.initialFilters.isSearchAroundMe = true

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const slider = wrapper.find(Slider)
            expect(slider).toHaveLength(1)
            expect(slider.prop('max')).toStrictEqual(100)
            expect(slider.prop('min')).toStrictEqual(0)
            expect(slider.prop('onChange')).toStrictEqual(expect.any(Function))
            expect(slider.prop('onAfterChange')).toStrictEqual(expect.any(Function))
            expect(slider.prop('value')).toStrictEqual(20)
          })
        })
      })

      describe('offer type', () => {
        it('should display a "Type d\'offres" title for offer types filter', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.find({ children: "Type d'offres" })
          expect(title).toHaveLength(1)
        })

        it('should render three FilterCheckbox components unchecked by default', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerTypes = {
            isDigital: false,
            isEvent: false,
            isThing: false,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const filterCheckboxes = wrapper
            .find('[data-test="sf-offer-types-filter-wrapper"]')
            .find(FilterCheckbox)
          expect(filterCheckboxes).toHaveLength(3)
          expect(filterCheckboxes.at(0).prop('checked')).toBe(false)
          expect(filterCheckboxes.at(0).prop('className')).toBe('fc-label')
          expect(filterCheckboxes.at(0).prop('id')).toBe('isDigital')
          expect(filterCheckboxes.at(0).prop('label')).toBe('Offres numériques')
          expect(filterCheckboxes.at(0).prop('name')).toBe('isDigital')
          expect(filterCheckboxes.at(0).prop('onChange')).toStrictEqual(expect.any(Function))
          expect(filterCheckboxes.at(1).prop('checked')).toBe(false)
          expect(filterCheckboxes.at(1).prop('className')).toBe('fc-label')
          expect(filterCheckboxes.at(1).prop('id')).toBe('isThing')
          expect(filterCheckboxes.at(1).prop('label')).toBe('Offres physiques')
          expect(filterCheckboxes.at(1).prop('name')).toBe('isThing')
          expect(filterCheckboxes.at(1).prop('onChange')).toStrictEqual(expect.any(Function))
          expect(filterCheckboxes.at(2).prop('checked')).toBe(false)
          expect(filterCheckboxes.at(2).prop('className')).toBe('fc-label')
          expect(filterCheckboxes.at(2).prop('id')).toBe('isEvent')
          expect(filterCheckboxes.at(2).prop('label')).toBe('Sorties')
          expect(filterCheckboxes.at(2).prop('name')).toBe('isEvent')
          expect(filterCheckboxes.at(2).prop('onChange')).toStrictEqual(expect.any(Function))
        })

        it('should render three FilterCheckbox components checked when offer types are checked', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerTypes = {
            isDigital: true,
            isEvent: true,
            isThing: true,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const filterCheckboxes = wrapper
            .find('[data-test="sf-offer-types-filter-wrapper"]')
            .find(FilterCheckbox)
          expect(filterCheckboxes.at(0).prop('checked')).toBe(true)
          expect(filterCheckboxes.at(0).prop('className')).toBe('fc-label-checked')
          expect(filterCheckboxes.at(1).prop('checked')).toBe(true)
          expect(filterCheckboxes.at(1).prop('className')).toBe('fc-label-checked')
          expect(filterCheckboxes.at(2).prop('checked')).toBe(true)
          expect(filterCheckboxes.at(2).prop('className')).toBe('fc-label-checked')
        })

        it('should display the number of offer types selected when checked', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerTypes = {
            isDigital: true,
            isEvent: true,
            isThing: true,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper.find({ children: '(3)' })
          expect(numberOfOfferTypesSelected).toHaveLength(1)
        })

        it('should not display the number of offer types selected when not checked', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerTypes = {
            isDigital: false,
            isEvent: false,
            isThing: false,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper.find({ children: '(3)' })
          expect(numberOfOfferTypesSelected).toHaveLength(0)
        })

        it('should fetch offers when clicking on digital offer type', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          const wrapper = shallow(<Filters {...props} />)
          const digitalFilter = wrapper
            .find('[data-test="sf-offer-types-filter-wrapper"]')
            .find(FilterCheckbox)
            .at(0)
          props.query.parse.mockReturnValue({
            'mots-cles': 'librairies',
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

          // when
          digitalFilter.simulate('change', {
            target: {
              name: 'isDigital',
              checked: true,
            },
          })

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 100,
            date: null,
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            isSearchAroundMe: false,
            keywords: 'librairies',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerTypes: {
              isDigital: true,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
        })
      })

      describe('offer duo', () => {
        it('should display a "Uniquement les offres duo" title for offer duo filter', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.find({ children: 'Uniquement les offres duo' })
          expect(title).toHaveLength(1)
        })

        it('should render a FilterToggle component for offer duo unchecked by default', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerIsDuo = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const filterOfferIsDuo = wrapper
            .find({ children: 'Uniquement les offres duo' })
            .closest('li')
            .find(FilterToggle)
          expect(filterOfferIsDuo).toHaveLength(1)
          expect(filterOfferIsDuo.prop('checked')).toBe(false)
          expect(filterOfferIsDuo.prop('id')).toBe('offerIsDuo')
          expect(filterOfferIsDuo.prop('name')).toBe('offerIsDuo')
          expect(filterOfferIsDuo.prop('onChange')).toStrictEqual(expect.any(Function))
          const offerIsDuoCounter = wrapper
            .find({ children: 'Uniquement les offres duo' })
            .closest('li')
            .find({ children: '(1)' })
          expect(offerIsDuoCounter).toHaveLength(0)
        })

        it('should fetch offers when clicking on offer duo', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          const wrapper = shallow(<Filters {...props} />)
          const offerIsDuoFilter = wrapper
            .find({ children: 'Uniquement les offres duo' })
            .closest('li')
            .find(FilterToggle)
          props.query.parse.mockReturnValue({})
          fetchAlgolia.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [],
                nbHits: 0,
                page: 0,
              })
            })
          )

          // when
          offerIsDuoFilter.simulate('change', {
            target: {
              name: 'offerIsDuo',
              checked: true,
            },
          })

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 100,
            date: null,
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            isSearchAroundMe: false,
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: true,
            offerIsFree: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
        })

        it('should display counter when offer duo is checked', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.query.parse.mockReturnValue({})
          fetchAlgolia.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [],
                nbHits: 0,
                page: 0,
              })
            })
          )
          const wrapper = shallow(<Filters {...props} />)
          const offerIsDuoFilter = wrapper
            .find({ children: 'Uniquement les offres duo' })
            .closest('li')
            .find(FilterToggle)

          // when
          offerIsDuoFilter.simulate('change', {
            target: {
              name: 'offerIsDuo',
              checked: true,
            },
          })

          // then
          const offerIsDuoCounter = wrapper
            .find({ children: 'Uniquement les offres duo' })
            .closest('li')
            .find({ children: '(1)' })
          expect(offerIsDuoCounter).toHaveLength(1)
        })
      })

      describe('offer price', () => {
        it('should display a "Uniquement les offres gratuites" title for offer free filter', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.find({ children: 'Uniquement les offres gratuites' })
          expect(title).toHaveLength(1)
        })

        it('should render a FilterToggle component for offer free unchecked by default', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerIsFree = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const filterOfferIsFree = wrapper
            .find({ children: 'Uniquement les offres gratuites' })
            .closest('li')
            .find(FilterToggle)
          expect(filterOfferIsFree).toHaveLength(1)
          expect(filterOfferIsFree.prop('checked')).toBe(false)
          expect(filterOfferIsFree.prop('id')).toBe('offerIsFree')
          expect(filterOfferIsFree.prop('name')).toBe('offerIsFree')
          expect(filterOfferIsFree.prop('onChange')).toStrictEqual(expect.any(Function))
          const offerIsFreeCounter = wrapper
            .find({ children: 'Uniquement les offres gratuites' })
            .closest('li')
            .find({ children: '(1)' })
          expect(offerIsFreeCounter).toHaveLength(0)
        })

        it('should fetch offers when clicking on offer free', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          const wrapper = shallow(<Filters {...props} />)
          const offerIsFreeFilter = wrapper
            .find({ children: 'Uniquement les offres gratuites' })
            .closest('li')
            .find(FilterToggle)
          props.query.parse.mockReturnValue({})
          fetchAlgolia.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [],
                nbHits: 0,
                page: 0,
              })
            })
          )

          // when
          offerIsFreeFilter.simulate('change', {
            target: {
              name: 'offerIsFree',
              checked: true,
            },
          })

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 100,
            date: null,
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            isSearchAroundMe: false,
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: true,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
        })

        describe('when free offers filter is off', () => {
          it('should display a "Prix" title', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFree = false

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const title = wrapper.find({ children: 'Prix' })
            expect(title).toHaveLength(1)
            const priceRangeCounter = wrapper
              .find({ children: 'Prix' })
              .closest('li')
              .find({ children: '(1)' })
            expect(priceRangeCounter).toHaveLength(0)
          })

          it('should display the price range value', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFree = false
            props.initialFilters.priceRange = [0, 45]

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const kilometersRadius = wrapper.find({ children: '0 € - 45 €' })
            expect(kilometersRadius).toHaveLength(1)
          })

          it('should render a Range slider component', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFree = false
            props.initialFilters.priceRange = [0, 45]

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const rangeSlider = wrapper.find(Range)
            expect(rangeSlider).toHaveLength(1)
            expect(rangeSlider.prop('allowCross')).toStrictEqual(false)
            expect(rangeSlider.prop('max')).toStrictEqual(500)
            expect(rangeSlider.prop('min')).toStrictEqual(0)
            expect(rangeSlider.prop('onChange')).toStrictEqual(expect.any(Function))
            expect(rangeSlider.prop('onAfterChange')).toStrictEqual(expect.any(Function))
            expect(rangeSlider.prop('value')).toStrictEqual([0, 45])
          })

          it('should render a counter next to "Price" if not default value', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.query.parse.mockReturnValue({})
            fetchAlgolia.mockReturnValue(
              new Promise(resolve => {
                resolve({
                  hits: [],
                  nbHits: 0,
                  page: 0,
                })
              })
            )
            const wrapper = shallow(<Filters {...props} />)
            const priceRangeSlider = wrapper
              .find({ children: 'Prix' })
              .closest('li')
              .find(Range)

            // when
            priceRangeSlider.simulate('change', [5, 15])

            // then
            const priceRangeCounter = wrapper
              .find({ children: 'Prix' })
              .closest('li')
              .find({ children: '(1)' })
            expect(priceRangeCounter).toHaveLength(1)
          })
        })

        describe('when free offers filter is on', () => {
          it('should display counter', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.query.parse.mockReturnValue({})
            fetchAlgolia.mockReturnValue(
              new Promise(resolve => {
                resolve({
                  hits: [],
                  nbHits: 0,
                  page: 0,
                })
              })
            )
            const wrapper = shallow(<Filters {...props} />)
            const offerIsFreeFilter = wrapper
              .find({ children: 'Uniquement les offres gratuites' })
              .closest('li')
              .find(FilterToggle)

            // when
            offerIsFreeFilter.simulate('change', {
              target: {
                name: 'offerIsFree',
                checked: true,
              },
            })

            // then
            const offerIsFreeCounter = wrapper
              .find({ children: 'Uniquement les offres gratuites' })
              .closest('li')
              .find({ children: '(1)' })
            expect(offerIsFreeCounter).toHaveLength(1)
          })

          it('should not display a "Prix" title', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFree = true

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const title = wrapper.find({ children: 'Prix' })
            expect(title).toHaveLength(0)
          })

          it('should not display the price range value', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFree = true
            props.initialFilters.priceRange = [5, 35]

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const kilometersRadius = wrapper.find({ children: '5 € - 35 €' })
            expect(kilometersRadius).toHaveLength(0)
          })

          it('should not render a Range slider component', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFree = true

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const rangeSlider = wrapper.find(Range)
            expect(rangeSlider).toHaveLength(0)
          })
        })
      })

      describe('offer categories', () => {
        it('should display an accessible "Catégories" title button', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const categoriesTitle = wrapper.find({ children: 'Catégories' })
          const categoriesTitleButton = wrapper.find('button[aria-label="Afficher les catégories"]')
          expect(categoriesTitle).toHaveLength(1)
          expect(categoriesTitleButton.prop('aria-label')).toBe('Afficher les catégories')
          expect(categoriesTitleButton.prop('aria-pressed')).toBe(true)
        })

        it('should not render FilterCheckbox component when categories filter toggled hidden', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = []
          const wrapper = shallow(<Filters {...props} />)
          const categoriesButton = wrapper.findWhere(node => node.text() === 'Catégories').first()
          const categoriesWrapper = wrapper.find('[data-test="sf-categories-filter-wrapper"]')
          const filterCheckboxBeforeClick = categoriesWrapper.find(FilterCheckbox)
          const categoriesButtonClassNameBeforeClick = categoriesButton.prop('className')

          // when
          categoriesButton.simulate('click')

          // then
          const categoriesWrapperAfterClick = wrapper.find(
            '[data-test="sf-categories-filter-wrapper"]'
          )
          const filterCheckboxAfterClick = categoriesWrapperAfterClick.find(FilterCheckbox)
          expect(filterCheckboxBeforeClick).toHaveLength(11)
          expect(filterCheckboxAfterClick).toHaveLength(0)

          const categoriesButtonAfterClick = wrapper
            .findWhere(node => node.text() === 'Catégories')
            .at(1)
          expect(categoriesButtonClassNameBeforeClick).toBe(
            'sf-category-title-wrapper sf-title-drop-down'
          )
          expect(categoriesButtonAfterClick.prop('className')).toBe(
            'sf-category-title-wrapper sf-title-drop-down-flipped'
          )
        })

        it('should render one unchecked FilterCheckbox component for each Category Criteria when no category is selected', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = []

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const cinemaFilterCheckbox = wrapper.find('FilterCheckbox[label="Cinéma"]')
          expect(cinemaFilterCheckbox.prop('checked')).toBe(false)
          expect(cinemaFilterCheckbox.prop('className')).toBe('fc-label')
          expect(cinemaFilterCheckbox.prop('id')).toBe('CINEMA')
          expect(cinemaFilterCheckbox.prop('label')).toBe('Cinéma')
          expect(cinemaFilterCheckbox.prop('name')).toBe('CINEMA')
          expect(cinemaFilterCheckbox.prop('onChange')).toStrictEqual(expect.any(Function))
          expect(wrapper.find('FilterCheckbox[label="Visites, expositions"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('FilterCheckbox[label="Musique"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Spectacles"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Cours, ateliers"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('FilterCheckbox[label="Livres"]').prop('checked')).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Films, séries, podcasts"]').prop('checked')
          ).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Presse"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Jeux vidéos"]').prop('checked')).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Conférences, rencontres"]').prop('checked')
          ).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Instruments de musique"]').prop('checked')
          ).toBe(false)
        })

        it('should not render FilterCheckbox component for "Toutes les catégories" Criteria', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = []

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const allCategoriesFilterCheckbox = wrapper.find(
            'FilterCheckbox[label="Toutes les catégories"]'
          )
          expect(allCategoriesFilterCheckbox).toHaveLength(0)
        })

        it('should render a FilterCheckbox component checked when category is selected', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = ['CINEMA', 'LIVRE']

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const cinemaCheckbox = wrapper.find('FilterCheckbox[label="Cinéma"]')
          expect(cinemaCheckbox.prop('checked')).toBe(true)
          expect(cinemaCheckbox.prop('className')).toBe('fc-label-checked')
          expect(wrapper.find('FilterCheckbox[label="Visites, expositions"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('FilterCheckbox[label="Musique"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Spectacles"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Cours, ateliers"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('FilterCheckbox[label="Livres"]').prop('checked')).toBe(true)
          expect(wrapper.find('FilterCheckbox[label="Livres"]').prop('className')).toBe(
            'fc-label-checked'
          )
          expect(
            wrapper.find('FilterCheckbox[label="Films, séries, podcasts"]').prop('checked')
          ).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Presse"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Jeux vidéos"]').prop('checked')).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Conférences, rencontres"]').prop('checked')
          ).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Instruments de musique"]').prop('checked')
          ).toBe(false)
        })

        it('should display the number of selected categories', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = ['CINEMA', 'LIVRE', 'VISITE']

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper.find({ children: '(3)' })
          expect(numberOfOfferTypesSelected).toHaveLength(1)
        })

        it('should not display the number of offer types selected when no filter is selected', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = []

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper.find({ children: '(0)' })
          expect(numberOfOfferTypesSelected).toHaveLength(0)
        })

        it('should transform array of categories received from props into an object in state', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = ['CINEMA', 'VISITE']

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          expect(wrapper.state().filters.offerCategories).toStrictEqual({
            CINEMA: true,
            VISITE: true,
          })
        })
      })

      describe('reset filters', () => {
        it('should reset filters and trigger search to Algolia with given categories when price range is selected', () => {
          // given
          props.history = createBrowserHistory()
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {
          })
          props.history.location.pathname = '/recherche/resultats/filtres'
          props.initialFilters = {
            date: {
              option: 'currentWeek',
              selectedDate: new Date(),
            },
            offerIsFilteredByDate: true,
            isSearchAroundMe: true,
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: true,
            offerIsFree: false,
            offerTypes: {
              isDigital: true,
              isEvent: true,
              isThing: true,
            },
            priceRange: [5, 40],
            sortBy: '_by_price',
          }
          props.query.parse.mockReturnValue({
            'mots-cles': 'librairie',
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
          const resetButton = wrapper
            .find(HeaderContainer)
            .find('.reset-button')
            .first()

          // when
          resetButton.simulate('click')

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 100,
            date: null,
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            isSearchAroundMe: false,
            keywords: 'librairie',
            offerCategories: [],
            offerIsDuo: false,
            offerIsFree: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
        })

        it('should reset filters and trigger search to Algolia with given categories when offer is free is selected', () => {
          // given
          props.history = createBrowserHistory()
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {
          })
          props.history.location.pathname = '/recherche/resultats/filtres'
          props.initialFilters = {
            date: {
              option: 'currentWeek',
              selectedDate: new Date(),
            },
            offerIsFilteredByDate: true,
            isSearchAroundMe: true,
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: true,
            offerIsFree: true,
            offerTypes: {
              isDigital: true,
              isEvent: true,
              isThing: true,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          }
          props.query.parse.mockReturnValue({
            'mots-cles': 'librairie',
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
          const resetButton = wrapper
            .find(HeaderContainer)
            .find('.reset-button')
            .first()

          // when
          resetButton.simulate('click')

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 100,
            date: null,
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            isSearchAroundMe: false,
            keywords: 'librairie',
            offerCategories: [],
            offerIsDuo: false,
            offerIsFree: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
        })
      })

      describe('date filters', () => {
        it('should render a FilterToggle component for date filter unchecked by default', () => {
          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const parentLi = wrapper.find({ children: 'Date' }).closest('li')
          const dateFilterToggle = parentLi.find(FilterToggle)
          expect(dateFilterToggle).toHaveLength(1)
          expect(dateFilterToggle.prop('checked')).toBe(false)
          expect(dateFilterToggle.prop('id')).toBe('offerIsFilteredByDate')
          expect(dateFilterToggle.prop('name')).toBe('offerIsFilteredByDate')
          expect(dateFilterToggle.prop('onChange')).toStrictEqual(expect.any(Function))
          const dateFilterCounter = parentLi.find({ children: '(1)' })
          expect(dateFilterCounter).toHaveLength(0)
        })

        it('should render a list of date filters when date toggle is on', () => {
          // given
          const history = createBrowserHistory()
          history.push('/recherche/resultats/filtres')
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Filters {...props} />
              </Router>
            </Provider>
          )
          const toggle = wrapper.find('input[name="offerIsFilteredByDate"]')

          // when
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // then
          const today = wrapper.find({ children: 'Aujourd\'hui' })
          const thisWeek = wrapper.find({ children: 'Cette semaine' })
          const thisWeekend = wrapper.find({ children: 'Ce week-end' })
          const exactDate = wrapper.find({ children: 'Date précise' })

          expect(today).toHaveLength(1)
          expect(thisWeek).toHaveLength(1)
          expect(thisWeekend).toHaveLength(1)
          expect(exactDate).toHaveLength(1)
        })

        it('should render check icon when date filter is selected', () => {
          // given
          const history = createBrowserHistory()
          history.push('/recherche/resultats/filtres')
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Filters {...props} />
              </Router>
            </Provider>
          )
          const toggle = wrapper.find('input[name="offerIsFilteredByDate"]')
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })
          const defaultCheckedIcon = wrapper.find('label[htmlFor="today"]+Icon')

          // when
          const currentWeekend = wrapper.find('input[value="currentWeekEnd"]')
          currentWeekend.simulate('change', { target: { value: 'currentWeekEnd' } })
          const checkedIconAfterSelection = wrapper.find('label[htmlFor="current-week-end"]+Icon')

          // then
          expect(defaultCheckedIcon).toHaveLength(1)
          expect(checkedIconAfterSelection).toHaveLength(1)
        })

        it('should not render datepicker when filter date option is not "picked"', () => {
          // given
          const history = createBrowserHistory()
          history.push('/recherche/resultats/filtres')
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Filters {...props} />
              </Router>
            </Provider>
          )

          const toggle = wrapper.find('input[name="offerIsFilteredByDate"]')
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // when
          const currentWeekRadio = wrapper
            .find({ children: 'Cette semaine' })
            .closest('li')
            .find('input[type="radio"]')
          currentWeekRadio.simulate('change', { target: { value: 'currentWeek' } })

          // then
          const datepicker = wrapper.find('DatePicker')
          expect(datepicker).toHaveLength(0)
        })

        it('should display a counter when Date filter is toggled on', () => {
          // given
          const history = createBrowserHistory()
          history.push('/recherche/resultats/filtres')
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Filters {...props} />
              </Router>
            </Provider>
          )

          // when
          const toggle = wrapper.find('input[name="offerIsFilteredByDate"]')
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // then
          const numberOfDateSelected = wrapper.find({ children: '(1)' })
          expect(numberOfDateSelected).toHaveLength(1)
        })

        it('should fetch Algolia with date parameter set to today option', () => {
          // given
          const history = createBrowserHistory()
          history.push('/recherche/resultats/filtres')
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Filters {...props} />
              </Router>
            </Provider>
          )
          const toggle = wrapper.find('input[name="offerIsFilteredByDate"]')

          // when
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 100,
            date: {
              option: 'today',
              selectedDate: now,
            },
            isSearchAroundMe: false,
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
        })

        it('should fetch Algolia with date parameter set to currentWeek option', () => {
          // given
          const history = createBrowserHistory()
          history.push('/recherche/resultats/filtres')
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Filters {...props} />
              </Router>
            </Provider>
          )
          const toggle = wrapper.find('input[name="offerIsFilteredByDate"]')
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // when
          const currentWeekRadio = wrapper
            .find({ children: 'Cette semaine' })
            .closest('li')
            .find('input[type="radio"]')
          currentWeekRadio.simulate('change', { target: { value: 'currentWeek' } })

          // then
          expect(fetchAlgolia).toHaveBeenCalledTimes(2)
          expect(fetchAlgolia).toHaveBeenNthCalledWith(2, {
            aroundRadius: 100,
            date: {
              option: 'currentWeek',
              selectedDate: now,
            },
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            isSearchAroundMe: false,
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
        })

        it('should fetch Algolia with date parameter set to picked option', () => {
          // given
          global.Date = actualDate
          const history = createBrowserHistory()
          history.push('/recherche/resultats/filtres')
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Filters {...props} />
              </Router>
            </Provider>
          )
          const toggle = wrapper.find('input[name="offerIsFilteredByDate"]')
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          const pickedRadio = wrapper
            .find({ children: 'Date précise' })
            .closest('li')
            .find('input[type="radio"]')
          pickedRadio.simulate('change', { target: { value: 'picked' } })

          // when
          const datepicker = wrapper
            .find('DatePicker')
            .find({ role: 'option' })
            .last()
          datepicker.simulate('click')

          // Then
          expect(fetchAlgolia).toHaveBeenNthCalledWith(3, {
            aroundRadius: 100,
            date: {
              option: 'picked',
              selectedDate: expect.any(Date),
            },
            isSearchAroundMe: false,
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: [0, 500],
            sortBy: '_by_price',
          })
        })
      })
    })
  })
})
