import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import moment from 'moment'
import Slider, { Range } from 'rc-slider'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import { getStubStore } from '../../../../../utils/stubStore'
import { fetchAlgolia } from '../../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../../layout/Header/HeaderContainer'
import { Criteria } from '../../Criteria/Criteria'
import { GEOLOCATION_CRITERIA } from '../../Criteria/criteriaEnums'
import CriteriaLocation from '../../CriteriaLocation/CriteriaLocation'
import Checkbox from '../Checkbox/Checkbox'
import { Filters } from '../Filters'
import { PRICE_FILTER } from '../filtersEnums'
import { RadioList } from '../RadioList/RadioList'
import Toggle from '../Toggle/Toggle'

jest.mock('../../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn(),
}))

const scrollIntoRadioListRef = jest.fn()
const scrollIntoTimeRangeRef = jest.fn()
const stubRef = wrapper => {
  const instance = wrapper.instance()
  instance['radioListRef'] = {
    current: {
      scrollIntoView: scrollIntoRadioListRef,
    },
  }
  instance['timeRangeRef'] = {
    current: {
      scrollIntoView: scrollIntoTimeRangeRef,
    },
  }
}

describe('components | Filters', () => {
  const actualDate = global.Date
  const now = new Date(2020, 3, 14)
  const store = getStubStore({
    data: (state = {}) => state,
  })
  let props

  beforeEach(() => {
    props = {
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
        offerIsFilteredByTime: false,
        offerCategories: ['VISITE', 'CINEMA'],
        offerIsDuo: false,
        offerIsFree: false,
        offerIsNew: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        priceRange: PRICE_FILTER.DEFAULT_RANGE,
        searchAround: {
          everywhere: true,
          place: false,
          user: false,
        },
        timeRange: [8, 24],
      },
      match: {
        params: {},
      },
      nbHits: 0,
      place: null,
      parse: jest.fn(),
      showFailModal: jest.fn(),
      updateFilteredOffers: jest.fn(),
      updateFilters: jest.fn(),
      updateNumberOfActiveFilters: jest.fn(),
      updatePlace: jest.fn(),
      useAppSearch: false,
      userGeolocation: {
        latitude: 40,
        longitude: 41,
      },
    }
    props.parse.mockReturnValue({
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
    // eslint-disable-next-line jest/prefer-spy-on
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
      it('should render localisation filter page', () => {
        // given
        props.history.location.pathname = '/recherche/resultats/filtres/localisation'
        props.history.location.search = '?mots-cles=librairie'

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const criteria = wrapper.find(CriteriaLocation)
        expect(criteria).toHaveLength(1)
        expect(criteria.prop('activeCriterionLabel')).toStrictEqual('Partout')
        expect(criteria.prop('backTo')).toStrictEqual(
          '/recherche/resultats/filtres?mots-cles=librairie'
        )
        expect(criteria.prop('criteria')).toStrictEqual(GEOLOCATION_CRITERIA)
        expect(criteria.prop('geolocation')).toStrictEqual(props.userGeolocation)
        expect(criteria.prop('history')).toStrictEqual(props.history)
        expect(criteria.prop('match')).toStrictEqual(props.match)
        expect(criteria.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
        expect(criteria.prop('onPlaceSelection')).toStrictEqual(expect.any(Function))
        expect(criteria.prop('place')).toBeNull()
        expect(criteria.prop('title')).toStrictEqual('Localisation')
      })

      it('should render a CriteriaLocation component with "Partout" criterion when not searching around me', () => {
        // given
        props.history.location.pathname = '/recherche/resultats/filtres/localisation'

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const criteria = wrapper.find(CriteriaLocation)
        expect(criteria.prop('activeCriterionLabel')).toStrictEqual('Partout')
      })

      it('should trigger search and redirect to filters page when click on "Partout"', () => {
        // given
        props.history = createBrowserHistory()
        props.place = null
        jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
        jest.spyOn(props.history, 'push').mockImplementationOnce(() => {})
        props.history.location.pathname = '/recherche/resultats/filtres/localisation'
        props.parse.mockReturnValue({
          'autour-de': 'non',
          categories: 'VISITE;CINEMA',
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
        const everywhereButton = wrapper.find(Criteria).find('button').first()

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
          keywords: 'librairie',
          offerCategories: ['VISITE', 'CINEMA'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: false,
          timeRange: [],
        })
        expect(props.history.replace).toHaveBeenCalledWith({
          search:
            '?mots-cles=librairie&autour-de=non&categories=VISITE;CINEMA&latitude=40&longitude=41',
        })
        expect(props.history.push).toHaveBeenCalledWith(
          '/recherche/resultats/filtres?mots-cles=librairie&autour-de=non&categories=VISITE;CINEMA&latitude=40&longitude=41'
        )
      })

      it('should trigger search and redirect to filters page when click on "Autour de moi"', () => {
        // given
        props.history = createBrowserHistory()
        jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
        jest.spyOn(props.history, 'push').mockImplementationOnce(() => {})
        props.history.location.pathname = '/recherche/resultats/filtres/localisation'
        props.initialFilters.offerCategories = ['VISITE']
        props.parse.mockReturnValue({
          'autour-de': 'oui',
          categories: 'VISITE',
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
        const aroundMeButton = wrapper.find(Criteria).find('button').at(1)

        // when
        aroundMeButton.simulate('click')

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          date: null,
          geolocation: { latitude: 40, longitude: 41 },
          keywords: 'librairie',
          offerCategories: ['VISITE'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: true,
          timeRange: [],
        })
        expect(props.history.replace).toHaveBeenCalledWith({
          search: '?mots-cles=librairie&autour-de=oui&categories=VISITE&latitude=40&longitude=41',
        })
        expect(props.history.push).toHaveBeenCalledWith(
          '/recherche/resultats/filtres?mots-cles=librairie&autour-de=oui&categories=VISITE&latitude=40&longitude=41'
        )
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
        expect(header.prop('reset')).toStrictEqual(expect.any(Function))
        expect(header.prop('title')).toStrictEqual('Filtrer')
      })

      it('should display the number of results on the display results button', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.nbHits = 10

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const numberOfResults = wrapper.find({ children: 'Afficher les 10 résultats' })
        expect(numberOfResults).toHaveLength(1)
      })

      it('should display "999+" on the display results button when number of results exceeds 999', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.nbHits = 1000

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const numberOfResults = wrapper.find({ children: 'Afficher les 999+ résultats' })
        expect(numberOfResults).toHaveLength(1)
      })

      it('should pass the number of selected filters when clicking on the results button', () => {
        // given
        props.initialFilters.offerCategories = ['VISITE', 'CINEMA']
        props.initialFilters.offerIsFilteredByDate = true
        const history = createBrowserHistory()
        history.push('/recherche/resultats/filtres')
        props.parse.mockReturnValue({
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

      it('should pass place information when clicking on the results button', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.history.location.search = '?mots-cles=librairie'
        props.place = {
          geolocation: { latitude: 30, longitude: 2 },
          name: {
            long: 'Paris',
            short: 'Paris',
          },
        }
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.updatePlace).toHaveBeenCalledWith({
          geolocation: { latitude: 30, longitude: 2 },
          name: {
            long: 'Paris',
            short: 'Paris',
          },
        })
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
          offerIsFilteredByDate: true,
          offerIsFilteredByTime: false,
          date: {
            option: 'currentWeek',
            selectedDate,
          },
          offerCategories: ['VISITE', 'CINEMA'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: {
            everywhere: true,
            place: false,
            user: false,
          },
          timeRange: [8, 24],
        })
      })

      it('should not allow click on display results button when no results', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.parse.mockReturnValue({
          'mots-cles': 'librairies',
        })
        props.offers = {
          hits: [],
          nbHits: 0,
          page: 0,
        }
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(resultsButton.text()).toStrictEqual('Aucun résultat')
      })

      it('should display a warning message when searching around user', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        props.initialFilters.searchAround = {
          everywhere: false,
          place: false,
          user: true,
        }

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const message = wrapper.find({
          children: 'Seules les offres Sorties et Physiques seront affichées',
        })
        expect(message).toHaveLength(1)
      })

      it('should display a warning message when searching around a place', () => {
        // given
        props.place = {
          geolocation: { latitude: 40, longitude: 1 },
          name: {
            long: 'Paris',
            short: 'Paris',
          },
        }
        props.history.location.pathname = '/recherche/filtres'
        props.initialFilters.searchAround = {
          everywhere: false,
          place: true,
          user: false,
        }

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const message = wrapper.find({
          children: 'Seules les offres Sorties et Physiques seront affichées',
        })
        expect(message).toHaveLength(1)
      })

      it('should not display a warning message when not searching around user or place', () => {
        // given
        props.history.location.pathname = '/recherche/filtres'

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const message = wrapper.find({
          children: 'Seules les offres Sorties et Physiques seront affichées',
        })
        expect(message).toHaveLength(0)
      })

      it('should update offers to parent when using a filter', async () => {
        // given
        props.history.location.pathname = '/recherche/filtres'
        const wrapper = shallow(<Filters {...props} />)
        const offerIsDuoFilter = wrapper
          .find({ children: 'Uniquement les offres duo' })
          .closest('li')
          .find(Toggle)
        props.parse.mockReturnValue({})
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ name: 'offer1' }, { name: 'offer2' }],
              nbHits: 2,
              page: 0,
            })
          })
        )

        // when
        await offerIsDuoFilter.simulate('change', {
          target: {
            name: 'offerIsDuo',
            checked: true,
          },
        })

        // then
        expect(props.updateFilteredOffers).toHaveBeenCalledWith({
          hits: [{ name: 'offer1' }, { name: 'offer2' }],
          nbHits: 2,
          page: 0,
        })
      })

      describe('geolocation filter', () => {
        it('should display a "Localisation" title', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.find({ children: 'Localisation' })
          expect(title).toHaveLength(1)
        })

        it('should display a "Partout" title when initial filter is "Partout"', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.searchAround = {
            everywhere: true,
            place: false,
            user: false,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const button = wrapper.find({ children: 'Partout' })
          expect(button).toHaveLength(1)
        })

        it('should display a "Autour de moi" title when initial filter is "Autour de moi"', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.searchAround = {
            everywhere: false,
            place: false,
            user: true,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const button = wrapper.find({ children: 'Autour de moi' })
          expect(button).toHaveLength(1)
        })

        it('should display place name when initial filter is place', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.place = {
            geolocation: { latitude: 30, longitude: 2 },
            name: {
              long: "34 avenue de l'opéra, Paris",
              short: "34 avenue de l'opéra",
            },
          }
          props.initialFilters.searchAround = {
            everywhere: false,
            place: true,
            user: false,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const button = wrapper.find({ children: "34 avenue de l'opéra, Paris" })
          expect(button).toHaveLength(1)
        })

        it('should redirect to localisation filter page with given query params when click on button', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.history.location.search = '?mots-cles=librairie'
          props.initialFilters.searchAround = {
            everywhere: false,
            place: false,
            user: true,
          }
          const wrapper = shallow(<Filters {...props} />)
          const geolocationButton = wrapper.find({ children: 'Autour de moi' })

          // when
          geolocationButton.simulate('click')

          // then
          expect(props.history.push).toHaveBeenCalledWith(
            '/recherche/resultats/filtres/localisation?mots-cles=librairie'
          )
        })

        it('should redirect to localisation filter page with no query params when click on button', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.searchAround = {
            everywhere: false,
            place: false,
            user: true,
          }
          const wrapper = shallow(<Filters {...props} />)
          const geolocationButton = wrapper.find({ children: 'Autour de moi' })

          // when
          geolocationButton.simulate('click')

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
            props.initialFilters.searchAround = {
              everywhere: true,
              place: false,
              user: false,
            }

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const kilometersRadius = wrapper.find({ children: '0 km' })
            expect(kilometersRadius).toHaveLength(0)
          })

          it('should not render a Slider component', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.searchAround = {
              everywhere: true,
              place: false,
              user: false,
            }

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
            props.initialFilters.searchAround = {
              everywhere: false,
              place: false,
              user: true,
            }

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
            props.initialFilters.searchAround = {
              everywhere: false,
              place: false,
              user: true,
            }

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
            props.initialFilters.searchAround = {
              everywhere: false,
              place: false,
              user: true,
            }

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

        describe('when geolocation filter is a place', () => {
          it('should display a "Rayon" title', () => {
            // given
            props.place = {
              geolocation: { latitude: 41, longitude: 2 },
              name: {
                long: 'Paris',
                short: 'Paris',
              },
            }
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.searchAround = {
              everywhere: false,
              place: true,
              user: false,
            }

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const title = wrapper.find({ children: 'Rayon' })
            expect(title).toHaveLength(1)
          })

          it('should display the kilometers radius value', () => {
            // given
            props.place = {
              geolocation: { latitude: 41, longitude: 2 },
              name: {
                long: 'Paris',
                short: 'Paris',
              },
            }
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.aroundRadius = 50
            props.initialFilters.searchAround = {
              everywhere: false,
              place: true,
              user: false,
            }

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const kilometersRadius = wrapper.find({ children: '50 km' })
            expect(kilometersRadius).toHaveLength(1)
          })

          it('should render a Slider component', () => {
            // given
            props.place = {
              geolocation: { latitude: 41, longitude: 2 },
              name: {
                long: 'Paris',
                short: 'Paris',
              },
            }
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.aroundRadius = 20
            props.initialFilters.searchAround = {
              everywhere: false,
              place: true,
              user: false,
            }

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

        it('should render three Checkbox components unchecked by default', () => {
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
            .find(Checkbox)
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

        it('should render three Checkbox components checked when offer types are checked', () => {
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
            .find(Checkbox)
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
            .find(Checkbox)
            .at(0)
          props.parse.mockReturnValue({
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
            keywords: 'librairies',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerIsNew: false,
            offerTypes: {
              isDigital: true,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [],
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

        it('should render a Toggle component for offer duo unchecked by default', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerIsDuo = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const filterOfferIsDuo = wrapper
            .find({ children: 'Uniquement les offres duo' })
            .closest('li')
            .find(Toggle)
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
            .find(Toggle)
          props.parse.mockReturnValue({})
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
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: true,
            offerIsFree: false,
            offerIsNew: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [],
          })
        })

        it('should display counter when offer duo is checked', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.parse.mockReturnValue({})
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
            .find(Toggle)

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

        it('should render a Toggle component for offer free unchecked by default', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerIsFree = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const filterOfferIsFree = wrapper
            .find({ children: 'Uniquement les offres gratuites' })
            .closest('li')
            .find(Toggle)
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
            .find(Toggle)
          props.parse.mockReturnValue({})
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
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: true,
            offerIsNew: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [],
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
            expect(rangeSlider.prop('max')).toStrictEqual(300)
            expect(rangeSlider.prop('min')).toStrictEqual(0)
            expect(rangeSlider.prop('onChange')).toStrictEqual(expect.any(Function))
            expect(rangeSlider.prop('onAfterChange')).toStrictEqual(expect.any(Function))
            expect(rangeSlider.prop('value')).toStrictEqual([0, 45])
          })

          it('should render a counter next to "Price" if not default value', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.parse.mockReturnValue({})
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
            const priceRangeSlider = wrapper.find({ children: 'Prix' }).closest('li').find(Range)

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
            props.parse.mockReturnValue({})
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
              .find(Toggle)

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

        it('should not render Checkbox component when categories filter toggled hidden', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = []
          const wrapper = shallow(<Filters {...props} />)
          const categoriesButton = wrapper.findWhere(node => node.text() === 'Catégories').first()
          const categoriesWrapper = wrapper.find('[data-test="sf-categories-filter-wrapper"]')
          const filterCheckboxBeforeClick = categoriesWrapper.find(Checkbox)
          const categoriesButtonClassNameBeforeClick = categoriesButton.prop('className')

          // when
          categoriesButton.simulate('click')

          // then
          const categoriesWrapperAfterClick = wrapper.find(
            '[data-test="sf-categories-filter-wrapper"]'
          )
          const filterCheckboxAfterClick = categoriesWrapperAfterClick.find(Checkbox)
          expect(filterCheckboxBeforeClick).toHaveLength(12)
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

        it('should render one unchecked Checkbox component for each Category Criteria when no category is selected', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = []

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const cinemaFilterCheckbox = wrapper.find('Checkbox[label="Cinéma"]')
          expect(cinemaFilterCheckbox.prop('checked')).toBe(false)
          expect(cinemaFilterCheckbox.prop('className')).toBe('fc-label')
          expect(cinemaFilterCheckbox.prop('id')).toBe('CINEMA')
          expect(cinemaFilterCheckbox.prop('label')).toBe('Cinéma')
          expect(cinemaFilterCheckbox.prop('name')).toBe('CINEMA')
          expect(cinemaFilterCheckbox.prop('onChange')).toStrictEqual(expect.any(Function))
          expect(wrapper.find('Checkbox[label="Visites, expositions"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Musique"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Spectacles"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Cours, ateliers"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Livres"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Films, séries, podcasts"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('Checkbox[label="Presse"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Jeux"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Conférences, rencontres"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('Checkbox[label="Instruments de musique"]').prop('checked')).toBe(
            false
          )
        })

        it('should not render Checkbox component for "Toutes les catégories" Criteria', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = []

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const allCategoriesFilterCheckbox = wrapper.find(
            'Checkbox[label="Toutes les catégories"]'
          )
          expect(allCategoriesFilterCheckbox).toHaveLength(0)
        })

        it('should render a Checkbox component checked when category is selected', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerCategories = ['CINEMA', 'LIVRE']

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const cinemaCheckbox = wrapper.find('Checkbox[label="Cinéma"]')
          expect(cinemaCheckbox.prop('checked')).toBe(true)
          expect(cinemaCheckbox.prop('className')).toBe('fc-label-checked')
          expect(wrapper.find('Checkbox[label="Visites, expositions"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Musique"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Spectacles"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Cours, ateliers"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Livres"]').prop('checked')).toBe(true)
          expect(wrapper.find('Checkbox[label="Livres"]').prop('className')).toBe(
            'fc-label-checked'
          )
          expect(wrapper.find('Checkbox[label="Films, séries, podcasts"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('Checkbox[label="Presse"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Jeux"]').prop('checked')).toBe(false)
          expect(wrapper.find('Checkbox[label="Conférences, rencontres"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('Checkbox[label="Instruments de musique"]').prop('checked')).toBe(
            false
          )
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
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
          props.history.location.pathname = '/recherche/resultats/filtres'
          props.initialFilters = {
            date: {
              option: 'currentWeek',
              selectedDate: new Date(),
            },
            offerIsFilteredByDate: true,
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: true,
            offerIsFree: false,
            offerIsNew: false,
            offerTypes: {
              isDigital: true,
              isEvent: true,
              isThing: true,
            },
            priceRange: [5, 40],
            searchAround: {
              everywhere: true,
              place: false,
              user: false,
            },
          }
          props.parse.mockReturnValue({
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
          const resetButton = wrapper.find(HeaderContainer).find('.reset-button').first()

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
            keywords: 'librairie',
            offerCategories: [],
            offerIsDuo: false,
            offerIsFree: false,
            offerIsNew: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [],
          })
        })

        it('should reset filters and trigger search to Algolia with given categories when offer is free is selected', () => {
          // given
          props.history = createBrowserHistory()
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {})
          props.history.location.pathname = '/recherche/resultats/filtres'
          props.initialFilters = {
            date: {
              option: 'currentWeek',
              selectedDate: new Date(),
            },
            offerIsFilteredByDate: true,
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: true,
            offerIsFree: true,
            offerIsNew: true,
            offerTypes: {
              isDigital: true,
              isEvent: true,
              isThing: true,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: {
              everywhere: true,
              place: false,
              user: false,
            },
          }
          props.parse.mockReturnValue({
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
          const resetButton = wrapper.find(HeaderContainer).find('.reset-button').first()

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
            keywords: 'librairie',
            offerCategories: [],
            offerIsDuo: false,
            offerIsFree: false,
            offerIsNew: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [],
          })
        })
      })

      describe('date filters', () => {
        it('should render a Toggle component for date filter unchecked by default', () => {
          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const parentLi = wrapper.find({ children: 'Date' }).closest('li')
          const dateFilterToggle = parentLi.find(Toggle)
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
          const wrapper = shallow(<Filters {...props} />)
          stubRef(wrapper)

          const toggle = wrapper.find({ children: 'Date' }).closest('li').find(Toggle)

          // when
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // then
          const dateFilters = wrapper.find(RadioList)

          expect(dateFilters).toHaveLength(1)
          expect(dateFilters.prop('date')).toStrictEqual({ option: 'today', selectedDate: now })
          expect(dateFilters.prop('onDateSelection')).toStrictEqual(expect.any(Function))
          expect(dateFilters.prop('onPickedDate')).toStrictEqual(expect.any(Function))
        })

        it('should display a counter when Date filter is toggled on', () => {
          // given
          const wrapper = shallow(<Filters {...props} />)
          stubRef(wrapper)

          // when
          const toggle = wrapper.find({ children: 'Date' }).closest('li').find(Toggle)
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // then
          const numberOfDateSelected = wrapper.find({ children: '(1)' })
          expect(numberOfDateSelected).toHaveLength(1)
        })

        it('should fetch offers with date parameter on date filter toggle', () => {
          // given
          const wrapper = shallow(<Filters {...props} />)
          stubRef(wrapper)

          // when
          const toggle = wrapper.find({ children: 'Date' }).closest('li').find(Toggle)
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // then
          expect(scrollIntoRadioListRef).toHaveBeenCalledTimes(1)
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 100,
            date: {
              option: 'today',
              selectedDate: now,
            },
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerIsNew: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [],
          })
        })

        it('should fetch offers with given date option', () => {
          // given
          global.Date = actualDate
          const wrapper = shallow(<Filters {...props} />)
          stubRef(wrapper)

          const toggle = wrapper.find({ children: 'Date' }).closest('li').find(Toggle)
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // when
          const pickedRadio = wrapper.find(RadioList)
          pickedRadio.prop('onDateSelection')({ target: { value: 'picked' } })

          // Then
          expect(scrollIntoRadioListRef).toHaveBeenCalledTimes(2)
          expect(fetchAlgolia).toHaveBeenNthCalledWith(2, {
            aroundRadius: 100,
            date: {
              option: 'picked',
              selectedDate: expect.any(Date),
            },
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerIsNew: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [],
          })
        })

        it('should convert moment to native js date when specific date is picked and fetch Algolia with it', () => {
          // given
          const wrapper = shallow(<Filters {...props} />)
          stubRef(wrapper)

          const toggle = wrapper.find({ children: 'Date' }).closest('li').find(Toggle)
          toggle.simulate('change', { target: { name: 'offerIsFilteredByDate', checked: true } })

          // when
          const pickedRadio = wrapper.find(RadioList)
          pickedRadio.prop('onPickedDate')(moment(now))

          // Then
          expect(fetchAlgolia).toHaveBeenNthCalledWith(2, {
            aroundRadius: 100,
            date: {
              option: 'picked',
              selectedDate: now,
            },
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerIsNew: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [],
          })
        })
      })

      describe('offer new', () => {
        it('should display a "Uniquement les nouveautés" title for offer is new filter', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.find({ children: 'Uniquement les nouveautés' })
          expect(title).toHaveLength(1)
        })

        it('should render a Toggle component for offer is new unchecked by default', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.initialFilters.offerIsNew = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const filterOfferIsNew = wrapper
            .find({ children: 'Uniquement les nouveautés' })
            .closest('li')
            .find(Toggle)
          expect(filterOfferIsNew).toHaveLength(1)
          expect(filterOfferIsNew.prop('checked')).toBe(false)
          expect(filterOfferIsNew.prop('id')).toBe('offerIsNew')
          expect(filterOfferIsNew.prop('name')).toBe('offerIsNew')
          expect(filterOfferIsNew.prop('onChange')).toStrictEqual(expect.any(Function))
          const offerIsNewCounter = wrapper
            .find({ children: 'Uniquement les nouveautés' })
            .closest('li')
            .find({ children: '(1)' })
          expect(offerIsNewCounter).toHaveLength(0)
        })

        it('should fetch offers when clicking on offer is new', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          const wrapper = shallow(<Filters {...props} />)
          const offerIsNewFilter = wrapper
            .find({ children: 'Uniquement les nouveautés' })
            .closest('li')
            .find(Toggle)
          props.parse.mockReturnValue({})
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
          offerIsNewFilter.simulate('change', {
            target: {
              name: 'offerIsNew',
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
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerIsNew: true,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [],
          })
        })
      })

      describe('time filters', () => {
        it('should render a Toggle component for time filter unchecked by default', () => {
          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const parentLi = wrapper.find({ children: 'Heure précise' }).closest('li')
          const dateFilterToggle = parentLi.find(Toggle)
          expect(dateFilterToggle).toHaveLength(1)
          expect(dateFilterToggle.prop('checked')).toBe(false)
          expect(dateFilterToggle.prop('id')).toBe('offerIsFilteredByTime')
          expect(dateFilterToggle.prop('name')).toBe('offerIsFilteredByTime')
          expect(dateFilterToggle.prop('onChange')).toStrictEqual(expect.any(Function))
          const dateFilterCounter = parentLi.find({ children: '(1)' })
          expect(dateFilterCounter).toHaveLength(0)
        })

        it('should fetch offers with timeRange parameter on time filter toggle on', () => {
          // given
          const wrapper = shallow(<Filters {...props} />)
          stubRef(wrapper)

          // when
          const toggle = wrapper.find({ children: 'Heure précise' }).closest('li').find(Toggle)
          toggle.simulate('change', { target: { name: 'offerIsFilteredByTime', checked: true } })

          // then
          expect(scrollIntoTimeRangeRef).toHaveBeenCalledTimes(1)
          expect(fetchAlgolia).toHaveBeenCalledWith({
            aroundRadius: 100,
            date: null,
            geolocation: {
              latitude: 40,
              longitude: 41,
            },
            keywords: '',
            offerCategories: ['VISITE', 'CINEMA'],
            offerIsDuo: false,
            offerIsFree: false,
            offerIsNew: false,
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false,
            },
            priceRange: PRICE_FILTER.DEFAULT_RANGE,
            searchAround: false,
            timeRange: [8, 24],
          })
        })

        describe('when time filter is toggled on', () => {
          it('should display the time range value', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFilteredByTime = true
            props.initialFilters.timeRange = [8, 24]

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const kilometersRadius = wrapper.find({ children: '8h - 0h' })
            expect(kilometersRadius).toHaveLength(1)
          })

          it('should render a Range slider component', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFree = true
            props.initialFilters.offerIsFilteredByTime = true
            props.initialFilters.timeRange = [8, 24]

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const rangeSlider = wrapper.find(Range)
            expect(rangeSlider).toHaveLength(1)
            expect(rangeSlider.prop('allowCross')).toStrictEqual(false)
            expect(rangeSlider.prop('max')).toStrictEqual(24)
            expect(rangeSlider.prop('min')).toStrictEqual(0)
            expect(rangeSlider.prop('onChange')).toStrictEqual(expect.any(Function))
            expect(rangeSlider.prop('onAfterChange')).toStrictEqual(expect.any(Function))
            expect(rangeSlider.prop('value')).toStrictEqual([8, 24])
          })

          it('should fetch algolia on time slide', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.parse.mockReturnValue({})
            props.initialFilters.offerIsFilteredByTime = true
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
            const timeRangeSlider = wrapper
              .find({ children: 'Créneau horaire' })
              .closest('li')
              .find(Range)

            // when
            timeRangeSlider.simulate('change', [18, 22])
            timeRangeSlider.simulate('afterChange')

            // then
            expect(fetchAlgolia).toHaveBeenCalledWith({
              aroundRadius: 100,
              date: null,
              geolocation: {
                latitude: 40,
                longitude: 41,
              },
              keywords: '',
              offerCategories: ['VISITE', 'CINEMA'],
              offerIsDuo: false,
              offerIsFree: false,
              offerIsNew: false,
              offerTypes: {
                isDigital: false,
                isEvent: false,
                isThing: false,
              },
              priceRange: PRICE_FILTER.DEFAULT_RANGE,
              searchAround: false,
              timeRange: [18, 22],
            })
          })
        })

        describe('when time filter is toggled off', () => {
          it('should not display the time range value', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFilteredByTime = false
            props.initialFilters.timeRange = [8, 24]

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const kilometersRadius = wrapper.find({ children: '8h - 0h' })
            expect(kilometersRadius).toHaveLength(0)
          })

          it('should not render a Range slider component', () => {
            // given
            props.history.location.pathname = '/recherche/filtres'
            props.initialFilters.offerIsFree = true
            props.initialFilters.offerIsFilteredByTime = false
            props.initialFilters.timeRange = [8, 24]

            // when
            const wrapper = shallow(<Filters {...props} />)

            // then
            const rangeSlider = wrapper.find(Range)
            expect(rangeSlider).toHaveLength(0)
          })
        })

        it('should display counter when offer is new is checked', () => {
          // given
          props.history.location.pathname = '/recherche/filtres'
          props.parse.mockReturnValue({})
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
            .find({ children: 'Uniquement les nouveautés' })
            .closest('li')
            .find(Toggle)

          // when
          offerIsDuoFilter.simulate('change', {
            target: {
              name: 'offerIsNew',
              checked: true,
            },
          })

          // then
          const offerIsNewCounter = wrapper
            .find({ children: 'Uniquement les nouveautés' })
            .closest('li')
            .find({ children: '(1)' })
          expect(offerIsNewCounter).toHaveLength(1)
        })
      })
    })
  })
})
