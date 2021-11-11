import { mount, shallow } from 'enzyme'
import { createBrowserHistory, createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import { Router } from 'react-router-dom'
import { toast } from 'react-toastify'

import { isGeolocationEnabled } from '../../../../../utils/geolocation'
import { getStubStore } from '../../../../../utils/stubStore'
import { fetchAlgolia } from '../../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../../layout/Header/HeaderContainer'
import Spinner from '../../../../layout/Spinner/Spinner'
import { Filters } from '../../Filters/Filters'
import { PRICE_FILTER } from '../../Filters/filtersEnums'
import Header from '../../Header/Header'
import { EmptyResult } from '../EmptyResult/EmptyResult'
import Results from '../Results'
import Result from '../ResultsList/Result/Result'
import SearchAlgoliaDetailsContainer from '../ResultsList/ResultDetail/ResultDetailContainer'
import { ResultsList } from '../ResultsList/ResultsList'

jest.mock('../../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn(),
}))
jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
  },
}))
jest.mock('../../../../../utils/geolocation', () => {
  const geolocationModule = jest.requireActual('../../../../../utils/geolocation')
  return {
    ...geolocationModule,
    isGeolocationEnabled: jest.fn(),
  }
})

const stubRef = wrapper => {
  const instance = wrapper.instance()
  instance['inputRef'] = {
    current: {
      blur: jest.fn(),
    },
  }
}

describe('components | Results', () => {
  let fakeTracking
  let props
  let parse
  let replace
  let push
  let store

  beforeEach(() => {
    fakeTracking = {
      push: jest.fn(),
    }
    window._paq = fakeTracking

    push = jest.fn()
    parse = jest.fn().mockReturnValue({})
    replace = jest.fn()
    store = getStubStore({
      data: (state = {}) => state,
    })

    props = {
      criteria: {
        categories: [],
        searchAround: {
          everywhere: true,
          place: false,
          user: false,
        },
      },
      history: {
        location: {
          pathname: '/fake-url',
          search: '?mots-cles=librairie',
        },
        push,
        search: '',
        replace,
      },
      match: {
        params: {},
      },
      place: {
        geolocation: { latitude: null, longitude: null },
        name: null,
      },
      parse: parse,
      redirectToSearchMainPage: jest.fn(),
      useAppSearch: false,
      userGeolocation: {
        latitude: 40.1,
        longitude: 41.1,
      },
    }
    isGeolocationEnabled.mockReturnValue(true)
    fetchAlgolia.mockReturnValue(
      new Promise(resolve => {
        resolve({
          hits: [],
          nbHits: 0,
          nbPages: 0,
          page: 0,
        })
      })
    )
  })

  afterEach(() => {
    fetchAlgolia.mockReset()
    parse.mockReset()
    replace.mockReset()
  })
  describe('when mount', () => {
    it('should track keywords search when keywords and categories in url', () => {
      // given
      props.history = createMemoryHistory()
      props.history.push(
        '/recherche/resultats?categories=CINEMA&mots-cles=une%librairie&autour-de=oui'
      )

      parse.mockReturnValue({
        'autour-de': 'oui',
        categories: 'CINEMA',
        'mots-cles': 'une librairie',
      })

      // when
      shallow(<Results {...props} />)

      // then
      expect(fakeTracking.push).toHaveBeenCalledWith([
        'trackSiteSearch',
        'une librairie',
        'CINEMA',
        false,
      ])
    })

    it('should not track keywords search when no location.search', () => {
      // given
      props.history.location.search = null

      // when
      shallow(<Results {...props} />)

      // then
      expect(fakeTracking.push).not.toHaveBeenCalledWith()
    })

    describe('when no keywords in url', () => {
      it('should fetch data with page 0, given categories, geolocation around user', () => {
        props.criteria = {
          categories: ['Cinéma'],
          searchAround: {
            everywhere: false,
            place: false,
            user: true,
          },
        }

        // when
        shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: props.userGeolocation,
          keywords: '',
          offerCategories: ['Cinéma'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: true,
        })
      })
    })

    describe('when no results', () => {
      beforeEach(() => {
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [],
              page: 0,
              nbHits: 0,
              nbPages: 0,
              hitsPerPage: 2,
              processingTimeMS: 1,
              query: 'librairie',
              params: 'query=librairie&hitsPerPage=2',
            })
          })
        )
      })

      afterEach(() => {
        fetchAlgolia.mockReset()
        props.parse.mockReset()
      })

      it('should display EmptyResult component when 0 result', async () => {
        // given
        props.history = createMemoryHistory()
        props.history.push('/recherche/resultats')

        const wrapper = await mount(
          <Router history={props.history}>
            <Results {...props} />
          </Router>
        )

        stubRef(wrapper)
        const form = wrapper.find('form')

        // when
        await form.simulate('submit', {
          target: {
            keywords: {
              value: 'librairie',
            },
          },
          preventDefault: jest.fn(),
        })

        wrapper.update()

        // then
        const emptySearchResult = wrapper.find(EmptyResult)
        const filterButton = wrapper.find({ children: 'Filtrer' })
        expect(emptySearchResult).toHaveLength(1)
        expect(filterButton).toHaveLength(0)
        expect(emptySearchResult.prop('searchedKeywords')).toBe('librairie')
      })

      it('should fetch offers in all categories, without keyword, around user when clicking on "autour de chez toi"', async () => {
        // given
        const history = createMemoryHistory()
        props.history = history
        props.history.push(
          '/recherche/resultats?mots-cles=recherche%20sans%20résultat&autour-de=oui&categories=INSTRUMENT'
        )
        props.parse.mockReturnValue({
          'autour-de': 'oui',
          categories: 'INSTRUMENT',
          'mots-cles': 'recherche sans résultat',
        })
        const wrapper = await mount(
          <Router history={history}>
            <Results {...props} />
          </Router>
        )
        wrapper.update()
        const linkButton = wrapper.find({ children: 'autour de chez toi' })

        // when
        await linkButton.simulate('click')

        // then
        expect(fetchAlgolia).toHaveBeenNthCalledWith(2, {
          aroundRadius: 100,
          geolocation: {
            latitude: 40.1,
            longitude: 41.1,
          },
          keywords: '',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: true,
        })
        const expectedUri = props.history.location.pathname + props.history.location.search
        expect(expectedUri).toBe(
          '/recherche/resultats?mots-cles=&autour-de=oui&categories=&latitude=40.1&longitude=41.1'
        )
      })
    })

    describe('when keywords in url', () => {
      it('should fill search input, display keywords, number of results and fetch data with page 0', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4', offer: { dates: [1586248757] } }],
              nbHits: 1,
              nbPages: 1,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'autour-de': 'non',
          'mots-cles': 'une librairie',
        })
        props.history = createMemoryHistory()
        props.history.push(
          '/recherche/resultats?mots-cles=une%20librairie&autour-de=non&categories=INSTRUMENT'
        )
        const store = getStubStore({
          data: (state = {}) => state,
        })

        // when
        const wrapper = await mount(
          <Provider store={store}>
            <Router history={props.history}>
              <Results {...props} />
            </Router>
          </Provider>
        )

        wrapper.update()

        // then
        const searchResultsListComponent = wrapper.find(ResultsList)
        const results = searchResultsListComponent.prop('results')
        const searchInput = wrapper.find('input')
        expect(results).toHaveLength(1)
        expect(searchInput.prop('value')).toBe('une librairie')
        expect(searchResultsListComponent.prop('resultsCount')).toBe(1)
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: {
            latitude: 40.1,
            longitude: 41.1,
          },
          keywords: 'une librairie',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: false,
        })
      })

      it('should fill search input and display keywords, number of results when results are found', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [
                { objectID: '4', offer: { dates: [] } },
                { objectID: '5', offer: { dates: [] } },
              ],
              nbHits: 2,
              nbPages: 0,
              page: 0,
            })
          })
        )

        props.history = createMemoryHistory()
        props.history.push('/recherche/resultats?mots-cles=une%librairie&autour-de=oui')

        parse.mockReturnValue({
          'autour-de': 'oui',
          'mots-cles': 'une librairie',
        })
        const store = getStubStore({
          data: (state = {}) => state,
        })

        // when
        const wrapper = await mount(
          <Provider store={store}>
            <Router history={props.history}>
              <Results {...props} />
            </Router>
          </Provider>
        )
        wrapper.update()

        // then
        const searchResultsListComponent = wrapper.find(ResultsList)
        const results = searchResultsListComponent.prop('results')
        const searchInput = wrapper.find('input')
        expect(results).toHaveLength(2)
        expect(searchResultsListComponent.prop('resultsCount')).toBe(2)
        expect(searchResultsListComponent.prop('geolocation')).toStrictEqual(props.userGeolocation)
        expect(searchResultsListComponent.prop('results')).toStrictEqual([
          { objectID: '4', offer: { dates: [] } },
          { objectID: '5', offer: { dates: [] } },
        ])
        expect(searchResultsListComponent.prop('search')).toBe(props.history.location.search)
        expect(searchInput.prop('value')).toBe('une librairie')
      })
    })

    describe('when geolocation', () => {
      it('should fetch data using geolocation coordinates when geolocation is enabled', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 2,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'autour-de': 'oui',
          'mots-cles': 'une librairie',
        })

        // when
        shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: true,
        })
      })

      it('should replace "autour-de" query param from oui to non when geolocation is disabled', async () => {
        // given
        props.userGeolocation = {
          latitude: null,
          longitude: null,
        }
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [],
              nbHits: 0,
              nbPages: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'autour-de': 'oui',
        })
        isGeolocationEnabled.mockReturnValue(false)

        // when
        shallow(<Results {...props} />)

        // then
        expect(props.history.replace).toHaveBeenCalledWith({
          search: '?mots-cles=&autour-de=non&categories=',
        })
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: null, longitude: null },
          keywords: '',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: false,
        })
      })
    })

    describe('when category filter', () => {
      it('should fetch data filtered by categories from props when provided', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 2,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          categories: '',
          'mots-cles': 'une librairie',
        })
        props.criteria.categories = ['CINEMA']

        // when
        await shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: ['CINEMA'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: false,
        })
      })

      it('should fetch data filtered by categories from URL when provided', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'autour-de': 'oui',
          categories: 'CINEMA',
          'mots-cles': 'une librairie',
        })
        props.criteria = {}

        // when
        await shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: ['CINEMA'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: { isDigital: false, isEvent: false, isThing: false },
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          page: 0,
          searchAround: true,
        })
      })

      it('should fetch data filtered by categories from URL when both from props and URL are provided', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 2,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          categories: 'CINEMA',
          'mots-cles': 'une librairie',
        })
        props.criteria.categories = ['VISITE']

        // when
        await shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: ['CINEMA'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: { isDigital: false, isEvent: false, isThing: false },
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          page: 0,
          searchAround: false,
        })
      })

      it('should fetch data with empty category filter when no category in URL nor props provided', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [],
              nbHits: 0,
              nbPages: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          categories: '',
          'mots-cles': 'une librairie',
        })

        // when
        await shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: false,
        })
      })
    })

    describe('when coming from home page', () => {
      it('should fetch data using filters from homepage', async () => {
        // given
        props.parametersFromHome = {
          aroundRadius: 1,
          geolocation: { latitude: 1, longitude: 1 },
          hitsPerPage: 2,
          offerCategories: ['SPECTACLE'],
          offerIsDuo: false,
          offerIsNew: false,
          offerTypes: { isDigital: false, isEvent: true, isThing: false },
          priceRange: [1, 200],
          searchAround: false,
        }
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'mots-cles': '',
        })

        // when
        await shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 1,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: '',
          offerCategories: ['SPECTACLE'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: true,
            isThing: false,
          },
          page: 0,
          priceRange: [1, 200],
          searchAround: false,
        })
      })

      it('should display number of active filters according to parameters from homepage', async () => {
        // given
        props.parametersFromHome = {
          aroundRadius: 100,
          geolocation: { latitude: 1, longitude: 1 },
          hitsPerPage: 2,
          offerCategories: ['SPECTACLE'],
          offerIsDuo: false,
          offerIsNew: false,
          offerTypes: { isDigital: false, isEvent: false, isThing: false },
          priceRange: [1, 200],
          searchAround: false,
        }
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'mots-cles': '',
        })

        // when
        const wrapper = await shallow(<Results {...props} />)

        // then
        const numberOfActiveFilters = wrapper.find('[data-test="sr-filter-button-counter"]')
        expect(numberOfActiveFilters.text()).toBe('2')
      })
    })
  })

  describe('when render', () => {
    it('should display a header with the right properties on details', () => {
      // when
      const wrapper = shallow(<Results {...props} />)

      // then
      const header = wrapper.find(HeaderContainer)
      expect(header).toHaveLength(1)
      expect(header.prop('backActionOnClick')).toStrictEqual(
        wrapper.instance().retrieveScrollPosition
      )
      expect(header.prop('shouldBackFromDetails')).toBe(true)
      expect(header.prop('title')).toBe('Recherche')
    })

    it('should display a form element with an input text', async () => {
      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=recherche')

      const wrapper = await mount(
        <Router history={props.history}>
          <Results {...props} />
        </Router>
      )

      // then
      const form = wrapper.find('form')
      expect(form).toHaveLength(1)
      const textInput = form.find('input')
      expect(textInput).toHaveLength(1)
      expect(textInput.prop('name')).toBe('keywords')
      expect(textInput.prop('placeholder')).toBe('Titre, artiste...')
      expect(textInput.prop('type')).toBe('search')
    })

    it('should display a filter button', () => {
      // when
      const wrapper = shallow(<Results {...props} />)

      // then
      const filterButton = wrapper.find({ children: 'Filtrer' })
      expect(filterButton).toHaveLength(1)
    })

    it('should display the number of selected filters in the filter button', () => {
      //given
      props.criteria.searchAround = {
        everywhere: false,
        place: false,
        user: true,
      }
      props.criteria.categories = ['CINEMA']

      // when
      const wrapper = shallow(<Results {...props} />)
      const numberOfActiveFilters = wrapper.find('[data-test="sr-filter-button-counter"]')

      // then
      expect(numberOfActiveFilters.text()).toStrictEqual('2')
    })

    it('should display the number of selected filters in the filter button when categories are provided by the url', () => {
      //given
      props.parse.mockReturnValue({
        'autour-de': 'oui',
        categories: 'CINEMA;VISITE',
      })

      // when
      const wrapper = shallow(<Results {...props} />)

      // then
      const numberOfActiveFilters = wrapper.find('[data-test="sr-filter-button-counter"]')
      expect(numberOfActiveFilters.text()).toStrictEqual('3')
    })

    it('should display the number of selected filters in the filter button when categories are provided by the url and props', () => {
      //given
      props.criteria.searchAround = {
        everywhere: false,
        place: false,
        user: true,
      }
      props.criteria.categories = ['CINEMA']
      props.parse.mockReturnValue({
        'autour-de': 'oui',
        categories: 'CINEMA;VISITE',
      })

      // when
      const wrapper = shallow(<Results {...props} />)
      const numberOfActiveFilters = wrapper.find('[data-test="sr-filter-button-counter"]')

      // then
      expect(numberOfActiveFilters.text()).toStrictEqual('3')
    })

    it('should display spinner while loading', () => {
      // when
      const wrapper = shallow(<Results {...props} />)

      // then
      expect(wrapper.find(Spinner)).toHaveLength(1)
    })

    it('should not display emptySearchResult component when loading', () => {
      // when
      const wrapper = shallow(<Results {...props} />)

      // then
      expect(wrapper.find(EmptyResult)).toHaveLength(0)
    })

    it('should not display spinner while loading is not over', async () => {
      // when
      const wrapper = await shallow(<Results {...props} />)

      // then
      expect(wrapper.find(Spinner)).toHaveLength(0)
    })

    it('should fetch data using query params when provided', async () => {
      // given
      fetchAlgolia.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [{ objectID: '4' }, { objectID: '5' }],
            nbHits: 2,
            nbPages: 0,
            page: 0,
          })
        })
      )
      props.criteria.searchAround = {
        everywhere: false,
        place: false,
        user: true,
      }
      parse.mockReturnValue({
        'autour-de': 'oui',
        categories: 'MUSEE',
        'mots-cles': 'une librairie',
      })
      props.criteria = {}

      // when
      await shallow(<Results {...props} />)

      // then
      expect(fetchAlgolia).toHaveBeenCalledWith({
        aroundRadius: 100,
        geolocation: {
          latitude: 40.1,
          longitude: 41.1,
        },
        keywords: 'une librairie',
        offerCategories: ['MUSEE'],
        offerIsDuo: false,
        offerIsFree: false,
        offerIsNew: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        page: 0,
        priceRange: PRICE_FILTER.DEFAULT_RANGE,
        searchAround: true,
      })
    })

    describe('when no keywords in url', () => {
      it('should fetch data with page 0, given categories, geolocation around user', () => {
        props.criteria = {
          categories: ['Cinéma'],
          searchAround: {
            everywhere: false,
            place: false,
            user: true,
          },
        }

        // when
        shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: props.userGeolocation,
          keywords: '',
          offerCategories: ['Cinéma'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: true,
        })
      })
    })

    describe('when no results', () => {
      beforeEach(() => {
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [],
              page: 0,
              nbHits: 0,
              nbPages: 0,
              hitsPerPage: 2,
              processingTimeMS: 1,
              query: 'librairie',
              params: 'query=librairie&hitsPerPage=2',
            })
          })
        )
      })

      afterEach(() => {
        fetchAlgolia.mockReset()
        props.parse.mockReset()
      })

      it('should display EmptyResult component when 0 result', async () => {
        // given
        props.history = createMemoryHistory()
        props.history.push('/recherche/resultats')

        const wrapper = await mount(
          <Router history={props.history}>
            <Results {...props} />
          </Router>
        )

        stubRef(wrapper)
        const form = wrapper.find('form')

        // when
        await form.simulate('submit', {
          target: {
            keywords: {
              value: 'librairie',
            },
          },
          preventDefault: jest.fn(),
        })

        wrapper.update()

        // then
        const emptySearchResult = wrapper.find(EmptyResult)
        const filterButton = wrapper.find({ children: 'Filtrer' })
        expect(emptySearchResult).toHaveLength(1)
        expect(filterButton).toHaveLength(0)
        expect(emptySearchResult.prop('searchedKeywords')).toBe('librairie')
      })

      it('should fetch offers in all categories, without keyword, around user when clicking on "autour de chez toi"', async () => {
        // given
        const history = createMemoryHistory()
        props.history = history
        props.history.push(
          '/recherche/resultats?mots-cles=recherche%20sans%20résultat&autour-de=oui&categories=INSTRUMENT'
        )
        props.parse.mockReturnValue({
          'autour-de': 'oui',
          categories: 'INSTRUMENT',
          'mots-cles': 'recherche sans résultat',
        })
        const wrapper = await mount(
          <Router history={history}>
            <Results {...props} />
          </Router>
        )
        wrapper.update()
        const linkButton = wrapper.find({ children: 'autour de chez toi' })

        // when
        await linkButton.simulate('click')

        // then
        expect(fetchAlgolia).toHaveBeenNthCalledWith(2, {
          aroundRadius: 100,
          geolocation: {
            latitude: 40.1,
            longitude: 41.1,
          },
          keywords: '',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: true,
        })
        const expectedUri = props.history.location.pathname + props.history.location.search
        expect(expectedUri).toBe(
          '/recherche/resultats?mots-cles=&autour-de=oui&categories=&latitude=40.1&longitude=41.1'
        )
      })
    })

    describe('when keywords in url', () => {
      it('should fill search input, display keywords, number of results and fetch data with page 0', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4', offer: { dates: [1586248757], subcategoryId: 'cinema' } }],
              nbHits: 1,
              nbPages: 1,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'autour-de': 'non',
          'mots-cles': 'une librairie',
        })
        props.history = createMemoryHistory()
        props.history.push(
          '/recherche/resultats?mots-cles=une%20librairie&autour-de=non&categories=INSTRUMENT'
        )

        const store = getStubStore({
          data: (state = {}) => state,
        })

        // when
        const wrapper = await mount(
          <Provider store={store}>
            <Router history={props.history}>
              <Results {...props} />
            </Router>
          </Provider>
        )

        wrapper.update()

        // then
        const searchResultsListComponent = wrapper.find(ResultsList)
        const results = searchResultsListComponent.prop('results')
        const searchInput = wrapper.find('input')
        expect(results).toHaveLength(1)
        expect(searchInput.prop('value')).toBe('une librairie')
        expect(searchResultsListComponent.prop('resultsCount')).toBe(1)
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: {
            latitude: 40.1,
            longitude: 41.1,
          },
          keywords: 'une librairie',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: false,
        })
      })

      it('should fill search input and display keywords, number of results when results are found', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [
                { objectID: '4', offer: { dates: [] } },
                { objectID: '5', offer: { dates: [] } },
              ],
              nbHits: 2,
              nbPages: 0,
              page: 0,
            })
          })
        )

        props.history = createMemoryHistory()
        props.history.push('/recherche/resultats?mots-cles=une%librairie&autour-de=oui')

        parse.mockReturnValue({
          'autour-de': 'oui',
          'mots-cles': 'une librairie',
        })

        const store = getStubStore({
          data: (state = {}) => state,
        })

        // when
        const wrapper = await mount(
          <Provider store={store}>
            <Router history={props.history}>
              <Results {...props} />
            </Router>
          </Provider>
        )

        wrapper.update()

        // then
        const searchResultsListComponent = wrapper.find(ResultsList)
        const results = searchResultsListComponent.prop('results')
        const searchInput = wrapper.find('input')
        expect(results).toHaveLength(2)
        expect(searchResultsListComponent.prop('resultsCount')).toBe(2)
        expect(searchResultsListComponent.prop('geolocation')).toStrictEqual(props.userGeolocation)
        expect(searchResultsListComponent.prop('results')).toStrictEqual([
          { objectID: '4', offer: { dates: [] } },
          { objectID: '5', offer: { dates: [] } },
        ])
        expect(searchResultsListComponent.prop('search')).toBe(props.history.location.search)
        expect(searchInput.prop('value')).toBe('une librairie')
      })
    })

    describe('when geolocation', () => {
      it('should fetch data using geolocation coordinates when geolocation is enabled', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 2,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'autour-de': 'oui',
          'mots-cles': 'une librairie',
        })

        // when
        shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: true,
        })
      })

      it('should replace "autour-de" query param from oui to non when geolocation is disabled', async () => {
        // given
        props.userGeolocation = {
          latitude: null,
          longitude: null,
        }
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [],
              nbHits: 0,
              nbPages: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'autour-de': 'oui',
        })
        isGeolocationEnabled.mockReturnValue(false)

        // when
        shallow(<Results {...props} />)

        // then
        expect(props.history.replace).toHaveBeenCalledWith({
          search: '?mots-cles=&autour-de=non&categories=',
        })
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: null, longitude: null },
          keywords: '',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: false,
        })
      })
    })

    describe('when category filter', () => {
      it('should fetch data filtered by categories from props when provided', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 2,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          categories: '',
          'mots-cles': 'une librairie',
        })
        props.criteria.categories = ['CINEMA']

        // when
        await shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: ['CINEMA'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: false,
        })
      })

      it('should fetch data filtered by categories from URL when provided', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'autour-de': 'oui',
          categories: 'CINEMA',
          'mots-cles': 'une librairie',
        })
        props.criteria = {}

        // when
        await shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: ['CINEMA'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: { isDigital: false, isEvent: false, isThing: false },
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          page: 0,
          searchAround: true,
        })
      })

      it('should fetch data filtered by categories from URL when both from props and URL are provided', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: '4' }, { objectID: '5' }],
              nbHits: 2,
              nbPages: 2,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          categories: 'CINEMA',
          'mots-cles': 'une librairie',
        })
        props.criteria.categories = ['VISITE']

        // when
        await shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: ['CINEMA'],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: { isDigital: false, isEvent: false, isThing: false },
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          page: 0,
          searchAround: false,
        })
      })

      it('should fetch data with empty category filter when no category in URL nor props provided', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [],
              nbHits: 0,
              nbPages: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          categories: '',
          'mots-cles': 'une librairie',
        })

        // when
        await shallow(<Results {...props} />)

        // then
        expect(fetchAlgolia).toHaveBeenCalledWith({
          aroundRadius: 100,
          geolocation: { latitude: 40.1, longitude: 41.1 },
          keywords: 'une librairie',
          offerCategories: [],
          offerIsDuo: false,
          offerIsFree: false,
          offerIsNew: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false,
          },
          page: 0,
          priceRange: PRICE_FILTER.DEFAULT_RANGE,
          searchAround: false,
        })
      })
    })
  })

  describe('when searching', () => {
    it('should trigger search request when keywords have been provided', () => {
      // given
      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=une%librairie&autour-de=oui')

      // when
      const wrapper = mount(
        <Router history={props.history}>
          <Results {...props} />
        </Router>
      )

      stubRef(wrapper)
      const form = wrapper.find('form')
      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: 'un livre très cherché',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      expect(fetchAlgolia).toHaveBeenCalledWith({
        aroundRadius: 100,
        geolocation: { latitude: 40.1, longitude: 41.1 },
        keywords: 'un livre très cherché',
        offerCategories: [],
        offerIsDuo: false,
        offerIsFree: false,
        offerIsNew: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        page: 0,
        priceRange: PRICE_FILTER.DEFAULT_RANGE,
        searchAround: false,
      })
    })

    it('should trigger search request when keywords contains only spaces', () => {
      // given
      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=une%librairie&autour-de=oui')

      // when
      const wrapper = mount(
        <Router history={props.history}>
          <Results {...props} />
        </Router>
      )

      stubRef(wrapper)
      wrapper.find(Results).setState({ searchedKeywords: 'une librairie' })
      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: ' ',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      expect(fetchAlgolia).toHaveBeenNthCalledWith(2, {
        aroundRadius: 100,
        geolocation: { latitude: 40.1, longitude: 41.1 },
        keywords: '',
        offerCategories: [],
        offerIsDuo: false,
        offerIsFree: false,
        offerIsNew: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        page: 0,
        priceRange: PRICE_FILTER.DEFAULT_RANGE,
        searchAround: false,
      })
    })

    it('should trigger search request when no keywords', () => {
      // given
      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=une%librairie&autour-de=oui')

      // when
      const wrapper = mount(
        <Router history={props.history}>
          <Results {...props} />
        </Router>
      )

      stubRef(wrapper)
      wrapper.find(Results).setState({ searchedKeywords: 'une librairie' })
      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: '',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      expect(fetchAlgolia).toHaveBeenCalledWith({
        aroundRadius: 100,
        geolocation: { latitude: 40.1, longitude: 41.1 },
        keywords: '',
        offerCategories: [],
        offerIsDuo: false,
        offerIsFree: false,
        offerIsNew: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        page: 0,
        priceRange: PRICE_FILTER.DEFAULT_RANGE,
        searchAround: false,
      })
    })

    it('should not display results when no results', () => {
      // given
      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=une%librairie&autour-de=oui')

      // when
      const wrapper = mount(
        <Router history={props.history}>
          <Results {...props} />
        </Router>
      )

      stubRef(wrapper)
      const form = wrapper.find('form')
      fetchAlgolia.mockReturnValue({
        hits: [],
        page: 0,
        nbHits: 0,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: '',
        params: 'hitsPerPage=2',
      })

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: '',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      const results = wrapper.find(Result)
      expect(results).toHaveLength(0)
    })

    it('should display results when search succeeded with at least one result', async () => {
      // given
      const offer = { objectID: '1', offer: { name: 'Livre de folie' } }
      fetchAlgolia
        .mockReturnValueOnce(
          new Promise(resolve => {
            resolve({
              hits: [],
              page: 0,
              nbHits: 0,
              nbPages: 0,
              hitsPerPage: 2,
              processingTimeMS: 1,
              query: 'une librairie',
              params: "query='librairie'&hitsPerPage=2",
            })
          })
        )
        .mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [offer],
              page: 0,
              nbHits: 1,
              nbPages: 1,
              hitsPerPage: 2,
              processingTimeMS: 1,
              query: 'librairie',
              params: "query='librairie'&hitsPerPage=2",
            })
          })
        )

      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=une%20librairie')

      parse.mockReturnValue({
        'mots-cles': 'une librairie',
        'autour-de': 'oui',
        latitude: 40.1,
        longitude: 41.1,
      })

      const wrapper = await mount(
        <Provider store={store}>
          <Router history={props.history}>
            <Results {...props} />
          </Router>
        </Provider>
      )

      const resultsWrapper = wrapper.find(Results)
      stubRef(resultsWrapper)
      const form = wrapper.find('form')

      // when
      await form.simulate('submit', {
        target: {
          keywords: {
            value: 'librairie',
          },
        },
        preventDefault: jest.fn(),
      })

      wrapper.update()

      // then
      const results = wrapper.find(ResultsList)
      expect(results).toHaveLength(1)
      expect(results.at(0).prop('currentPage')).toStrictEqual(0)
      expect(results.at(0).prop('geolocation')).toStrictEqual({ latitude: 40.1, longitude: 41.1 })
      expect(results.at(0).prop('isLoading')).toStrictEqual(false)
      expect(results.at(0).prop('loadMore')).toStrictEqual(expect.any(Function))
      expect(results.at(0).prop('results')).toStrictEqual([offer])
      expect(results.at(0).prop('resultsCount')).toStrictEqual(1)
      expect(results.at(0).prop('search')).toStrictEqual(
        '?mots-cles=librairie&autour-de=oui&categories=&latitude=40.1&longitude=41.1'
      )
      expect(results.at(0).prop('totalPagesNumber')).toStrictEqual(1)
    })

    it('should clear previous results and page number when searching with new keywords', async () => {
      // given
      isGeolocationEnabled.mockReturnValue(false)

      const offer1 = { objectID: '1', offer: { name: 'Livre de folie' } }
      const offer2 = { objectID: '2', offer: { name: 'Livre bien' } }
      const offer3 = { objectID: '3', offer: { name: 'Livre nul' } }

      fetchAlgolia.mockReturnValueOnce(
        new Promise(resolve => {
          resolve({
            hits: [],
            nbHits: 0,
          })
        })
      )

      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=une%20librairie')

      parse.mockReturnValue({
        'mots-cles': 'une librairie',
        'autour-de': 'oui',
        latitude: 40.1,
        longitude: 41.1,
      })

      const wrapper = await mount(
        <Provider store={store}>
          <Router history={props.history}>
            <Results {...props} />
          </Router>
        </Provider>
      )

      wrapper.update()

      const resultsWrapper = wrapper.find(Results)
      stubRef(resultsWrapper)
      const form = wrapper.find('form')

      fetchAlgolia.mockReturnValueOnce(
        new Promise(resolve => {
          resolve({
            hits: [offer1, offer2],
            page: 0,
            nbHits: 2,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'librairie',
            params: "query='librairie'&hitsPerPage=2",
          })
        })
      )

      // when
      await form.simulate('submit', {
        target: {
          keywords: {
            value: 'librairie',
          },
        },
        preventDefault: jest.fn(),
      })

      wrapper.update()

      // then
      const resultsFirstFetch = wrapper.find(ResultsList).prop('results')
      expect(resultsFirstFetch).toHaveLength(2)

      // when
      fetchAlgolia.mockReturnValueOnce(
        new Promise(resolve => {
          resolve({
            hits: [offer3],
            page: 0,
            nbHits: 1,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'vas-y',
            params: 'query="vas-y"&hitsPerPage=2',
          })
        })
      )
      await form.simulate('submit', {
        target: {
          keywords: {
            value: 'vas-y',
          },
        },
        preventDefault: jest.fn(),
      })

      wrapper.update()

      // then
      const resultSecondFetch = wrapper.find(ResultsList)
      expect(resultSecondFetch.prop('results')).toHaveLength(1)
      expect(wrapper.find(Results).state()).toStrictEqual({
        currentPage: 0,
        filters: {
          aroundRadius: 100,
          date: {
            option: 'today',
            selectedDate: null,
          },
          offerIsFilteredByDate: false,
          offerIsFilteredByTime: false,
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
          searchAround: {
            everywhere: true,
            place: false,
            user: false,
          },
          timeRange: [8, 24],
        },
        keywordsToSearch: 'vas-y',
        isLoading: false,
        numberOfActiveFilters: 0,
        place: {
          geolocation: { latitude: null, longitude: null },
          name: null,
        },
        results: [{ objectID: '3', offer: { name: 'Livre nul' } }],
        resultsCount: 1,
        searchedKeywords: 'vas-y',
        totalPagesNumber: 0,
      })
    })

    it('should not trigger a second search request when submitting same keywords twice', async () => {
      // given
      const offer1 = { objectID: '1', offer: { name: 'Livre de folie de la librairie' } }
      const offer2 = { objectID: '2', offer: { name: 'Livre bien de la librairie' } }
      fetchAlgolia.mockReturnValueOnce(
        new Promise(resolve => {
          resolve({
            hits: [offer1, offer2],
            page: 0,
            nbHits: 1,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'librairie',
            params: 'query=librairie&hitsPerPage=2',
          })
        })
      )

      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=librairie')

      parse.mockReturnValue({
        'mots-cles': 'librairie',
        'autour-de': 'oui',
        latitude: 40.1,
        longitude: 41.1,
      })

      const wrapper = await mount(
        <Provider store={store}>
          <Router history={props.history}>
            <Results {...props} />
          </Router>
        </Provider>
      )
      const resultsWrapper = wrapper.find(Results)
      stubRef(resultsWrapper)
      const form = wrapper.find('form')

      // when
      await form.simulate('submit', {
        target: {
          keywords: {
            value: 'librairie',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      expect(fetchAlgolia).toHaveBeenCalledTimes(1)
      expect(fetchAlgolia).toHaveBeenNthCalledWith(1, {
        aroundRadius: 100,
        geolocation: { latitude: 40.1, longitude: 41.1 },
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
        page: 0,
        priceRange: PRICE_FILTER.DEFAULT_RANGE,
        searchAround: true,
      })
    })

    it('should display an error when search failed', async () => {
      // given
      fetchAlgolia.mockReturnValue(
        new Promise(reject => {
          reject()
        })
      )

      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=librairie')

      parse.mockReturnValue({
        'mots-cles': 'librairie',
      })

      const wrapper = await mount(
        <Router history={props.history}>
          <Results {...props} />
        </Router>
      )

      stubRef(wrapper)

      await wrapper.update()

      // then
      expect(toast.error).toHaveBeenCalledWith(
        "La recherche n'a pas pu aboutir, réessaie plus tard."
      )
    })

    it('should call replace to display search keywords in url when fetch succeeded', () => {
      // given
      fetchAlgolia.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [],
            page: 0,
            nbHits: 0,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'librairie',
          })
        })
      )

      props.parse.mockReturnValue({
        'autour-de': 'oui',
        categories: 'VISITE',
        latitude: 40,
        longitude: 2,
        place: 'Paris',
      })

      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=tortue')
      props.history = {
        ...props.history,
        replace: jest.fn(),
      }

      const wrapper = mount(
        <Router history={props.history}>
          <Results {...props} />
        </Router>
      )

      stubRef(wrapper)

      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: 'librairie',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      expect(props.history.replace).toHaveBeenCalledWith({
        search:
          '?mots-cles=librairie&autour-de=oui&categories=VISITE&latitude=40&longitude=2&place=Paris',
      })
    })

    it('should remove focus from input when the form is submitted', () => {
      // given
      fetchAlgolia.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [],
            page: 0,
            nbHits: 0,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'tortue',
          })
        })
      )

      props.history = createMemoryHistory()
      props.history.push('/recherche/resultats?mots-cles=tortue')

      const wrapper = mount(
        <Router history={props.history}>
          <Results {...props} />
        </Router>
      )

      const resultsWrapper = wrapper.find(Results)
      const instance = resultsWrapper.instance()
      stubRef(resultsWrapper)
      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: '',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      expect(instance.inputRef.current.blur).toHaveBeenCalledWith()
    })

    it('should remove focus from input when scrolling the results', () => {
      // given
      const history = createBrowserHistory()
      history.push('/recherche/resultats')
      const wrapper = mount(
        <Router history={history}>
          <Results {...props} />
        </Router>
      )
      wrapper.setState({ isLoading: true })
      const searchResultsWrapper = wrapper.find(Results)
      const input = searchResultsWrapper.instance().inputRef.current
      jest.spyOn(input, 'blur').mockImplementationOnce()

      const searchResults = wrapper.find({ children: 'Recherche en cours' })

      // when
      searchResults.simulate('scroll')

      // then
      expect(input.blur).toHaveBeenCalledTimes(1)
    })

    it('should fetch algolia with date filter when enabled', async () => {
      // given
      const history = createBrowserHistory()
      history.push('/recherche/resultats')
      const wrapper = mount(
        <Router history={history}>
          <Results {...props} />
        </Router>
      )

      stubRef(wrapper)
      const selectedDate = new Date(2020, 3, 21)
      wrapper.find(Results).setState({
        filters: {
          ...wrapper.find(Results).state('filters'),
          date: {
            option: 'today',
            selectedDate,
          },
          offerIsFilteredByDate: true,
        },
      })

      // when
      const form = wrapper.find('form')
      form.simulate('submit', {
        preventDefault: jest.fn(),
        target: { keywords: { value: 'nouvelle recherche' } },
      })

      // then
      expect(fetchAlgolia).toHaveBeenCalledTimes(2)
      expect(fetchAlgolia).toHaveBeenNthCalledWith(2, {
        aroundRadius: 100,
        date: {
          option: 'today',
          selectedDate,
        },
        geolocation: {
          latitude: 40.1,
          longitude: 41.1,
        },
        keywords: 'nouvelle recherche',
        offerCategories: [],
        offerIsDuo: false,
        offerIsFree: false,
        offerIsNew: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false,
        },
        page: 0,
        priceRange: PRICE_FILTER.DEFAULT_RANGE,
        searchAround: false,
      })
    })

    it('should pass input value to Header when something is typed in text input', () => {
      // given
      const history = createBrowserHistory()
      history.push('/recherche/resultats')
      const wrapper = mount(
        <Router history={history}>
          <Results {...props} />
        </Router>
      )

      const form = wrapper.find('form')
      const input = form.find('input')

      // when
      input.simulate('change', {
        target: {
          name: 'keywords',
          value: 'tortue',
        },
        preventDefault: jest.fn(),
      })

      // then
      const headerWrapper = wrapper.find(Header)
      expect(headerWrapper.prop('value')).toBe('tortue')
    })

    it('should clear text input when clicking on reset cross', () => {
      // given
      const history = createMemoryHistory()
      history.push('/recherche/resultats?mots-cles=librairie&page=2')
      const wrapper = mount(
        <Router history={history}>
          <Results {...props} />
        </Router>
      )
      const form = wrapper.find('form')
      const input = form.find('input').first()
      input.simulate('change', {
        target: {
          name: 'keywords',
          value: 'typed search',
        },
      })
      const resetButton = wrapper.find('button[type="reset"]')

      // when
      resetButton.simulate('click')

      // then
      const expectedMissingResetButton = wrapper.find('button[type="reset"]')
      const resetInput = form.find('input').first()
      expect(expectedMissingResetButton).toHaveLength(0)
      expect(resetInput.prop('value')).toBe('')
    })
  })

  describe('when navigating', () => {
    let history
    let store

    beforeEach(() => {
      history = createMemoryHistory()
      store = getStubStore({
        data: (state = {}) => state,
      })
    })

    it('should render search main page when current route is /recherche/resultats', () => {
      // given
      history.push('/recherche/resultats')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Provider store={store}>
            <Results {...props} />
          </Provider>
        </Router>
      )

      // then
      const form = wrapper.find('form')
      const searchDetails = wrapper.find(SearchAlgoliaDetailsContainer)
      expect(form).toHaveLength(1)
      expect(searchDetails).toHaveLength(0)
    })

    it('should render item details when current route is /recherche/resultats/details/AE', () => {
      // given
      store = getStubStore({
        currentUser: (
          state = {
            id: 'Rt4R45ETEs',
            wallet_balance: 0,
          }
        ) => state,
        data: (
          state = {
            bookings: [],
            offers: [{ id: 'AE', name: 'Offer name example' }],
            stocks: [],
            favorites: [],
            features: [],
            mediations: [],
            users: [],
            categories: [
              {
                categories: [],
                subcategories: [],
              },
            ],
          }
        ) => state,
        geolocation: (
          state = {
            latitude: 1,
            longitude: 2,
          }
        ) => state,
      })

      // when
      const wrapper = mount(
        <MemoryRouter initialEntries={['/recherche/resultats/details/AE']}>
          <Provider store={store}>
            <Results {...props} />
          </Provider>
        </MemoryRouter>
      )

      // then
      const searchDetails = wrapper.find(SearchAlgoliaDetailsContainer)
      expect(searchDetails).toHaveLength(1)
    })

    it('should render filters page when current route is /recherche/resultats/filtres', () => {
      // given
      history.push('/recherche/resultats/filtres')
      props.parse.mockReturnValue({
        categories: 'VISITE;CINEMA',
        'mots-cles': 'librairie',
      })

      // when
      const wrapper = mount(
        <Router history={history}>
          <Provider store={store}>
            <Results {...props} />
          </Provider>
        </Router>
      )

      // then
      const filters = wrapper.find(Filters)
      expect(filters).toHaveLength(1)
      expect(filters.prop('history')).toStrictEqual(props.history)
      expect(filters.prop('initialFilters')).toStrictEqual({
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
      })
      expect(filters.prop('match')).toStrictEqual(props.match)
      expect(filters.prop('nbHits')).toStrictEqual(0)
      expect(filters.prop('place')).toStrictEqual(props.place)
      expect(filters.prop('parse')).toStrictEqual(props.parse)
      expect(filters.prop('showFailModal')).toStrictEqual(expect.any(Function))
      expect(filters.prop('updateFilteredOffers')).toStrictEqual(expect.any(Function))
      expect(filters.prop('updateFilters')).toStrictEqual(expect.any(Function))
      expect(filters.prop('updateNumberOfActiveFilters')).toStrictEqual(expect.any(Function))
      expect(filters.prop('updatePlace')).toStrictEqual(expect.any(Function))
      expect(filters.prop('useAppSearch')).toStrictEqual(props.useAppSearch)
      expect(filters.prop('userGeolocation')).toStrictEqual(props.userGeolocation)
    })

    describe('come back icon', () => {
      it('should render an icon to come back to search main page when a research has been made', () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [],
              nbHits: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'mots-cles': 'une librairie',
        })
        const history = createMemoryHistory()
        history.push('/recherche/resultats?mots-cles=une%20libriairie')

        // when
        const wrapper = mount(
          <Router history={history}>
            <Results {...props} />
          </Router>
        )

        // then
        const form = wrapper.find('form')
        const backIcon = form.findWhere(node => node.prop('svg') === 'picto-back-grey').first()
        expect(backIcon).toHaveLength(1)
      })

      it('should reset text input when clicking on come back arrow', async () => {
        // given
        fetchAlgolia.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [],
              nbHits: 0,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'mots-cles': 'une librairie',
        })
        const redirectToSearchMainPage = jest.fn()
        props.history = createMemoryHistory()
        props.history.push('/recherche/resultats?mots-cles=une%20librairie')

        // when
        const wrapper = await mount(
          <Router history={props.history}>
            <Results
              {...props}
              redirectToSearchMainPage={redirectToSearchMainPage}
            />
          </Router>
        )
        const resultsWrapper = wrapper.find(Results)
        const form = resultsWrapper.find('form')
        const backButton = form.findWhere(node => node.prop('type') === 'button').first()
        expect(resultsWrapper.state('keywordsToSearch')).toBe('une librairie')
        backButton.simulate('click')

        // then
        expect(redirectToSearchMainPage).toHaveBeenCalledTimes(1)
        expect(resultsWrapper.state('keywordsToSearch')).toBe('')
      })
    })

    describe('header', () => {
      it('should not render header when search has been made', () => {
        // given
        history.push('/recherche/resultats?mots-cles=librairie&page=1')
        const offer1 = { objectID: '1', offer: { name: 'Livre de folie de la librairie' } }
        const offer2 = { objectID: 'AY', offer: { name: 'Livre bien de la librairie' } }
        fetchAlgolia.mockReturnValueOnce(
          new Promise(resolve => {
            resolve({
              hits: [offer1, offer2],
              page: 0,
              nbHits: 1,
              nbPages: 0,
              hitsPerPage: 2,
              processingTimeMS: 1,
              query: 'librairie',
              params: 'query=librairie&hitsPerPage=2',
            })
          })
        )
        const wrapper = mount(
          <Router history={history}>
            <Results {...props} />
          </Router>
        )
        const form = wrapper.find('form')

        // when
        form.simulate('submit', {
          target: {
            keywords: {
              value: 'librairie',
            },
          },
          preventDefault: jest.fn(),
        })
        wrapper.update()

        // then
        const header = wrapper.find(HeaderContainer)
        expect(header).toHaveLength(0)
      })

      it('should render header when on details page', () => {
        // given
        store = getStubStore({
          currentUser: (
            state = {
              id: 'Rt4R45ETEs',
              wallet_balance: 0,
            }
          ) => state,
          data: (
            state = {
              bookings: [],
              offers: [{ id: 'AE', name: 'Offer name example' }],
              stocks: [],
              favorites: [],
              features: [],
              mediations: [],
              users: [],
              categories: [
                {
                  categories: [],
                  subcategories: [],
                },
              ],
            }
          ) => state,
          geolocation: (
            state = {
              latitude: 1,
              longitude: 2,
            }
          ) => state,
        })

        // when
        const wrapper = mount(
          <MemoryRouter
            initialEntries={['/recherche/resultats/details/AE?mots-cles=librairie&page=1']}
          >
            <Provider store={store}>
              <Results {...props} />
            </Provider>
          </MemoryRouter>
        )

        // then
        const header = wrapper.find(HeaderContainer)
        expect(header).toHaveLength(1)
      })
    })
  })

  describe('when filtering', () => {
    it('should redirect to filters page', () => {
      // given
      const history = createBrowserHistory()
      history.push('/recherche/resultats?mots-cles=librairie')
      props.history = history

      const wrapper = mount(
        <Provider store={store}>
          <Router history={history}>
            <Results {...props} />
          </Router>
        </Provider>
      )
      const filterButton = wrapper.find({ children: 'Filtrer' })

      // whensrc/components/pages/search/Results/__specs__/Results.spec.jsx
      filterButton.simulate('click')

      // then
      const expectedUrl = history.location.pathname + history.location.search
      expect(expectedUrl).toBe('/recherche/resultats/filtres?mots-cles=librairie')
    })
  })
})
