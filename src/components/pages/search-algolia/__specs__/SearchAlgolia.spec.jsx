import { createMemoryHistory } from 'history'
import { mount, shallow } from 'enzyme'
import { Provider } from 'react-redux'
import React from 'react'
import { Router } from 'react-router-dom'
import thunk from 'redux-thunk'

import configureStore from 'redux-mock-store'

import HeaderContainer from '../../../layout/Header/HeaderContainer'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import ResultsContainer from '../Results/ResultsContainer'
import SearchAlgolia from '../SearchAlgolia'
import SearchAlgoliaDetailsContainer from '../SearchAlgoliaDetailsContainer/SearchAlgoliaDetailsContainer'
import Spinner from '../../../layout/Spinner/Spinner'
import { fetch } from '../utils/algoliaService'

jest.mock('../utils/algoliaService', () => ({
  fetch: jest.fn()
}))

describe('src | components | pages | search-algolia | SearchAlgolia', () => {
  let props

  beforeEach(() => {
    props = {
      match: {
        params: {}
      }
    }
  })

  describe('render', () => {
    it('should display a header with the right properties', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const header = wrapper.find(HeaderContainer)
      expect(header).toHaveLength(1)
      expect(header.prop('title')).toBe('Recherche')
      expect(header.prop('backTo')).toBe(null)
      expect(header.prop('closeTitle')).toBe('Retourner à la page découverte')
      expect(header.prop('closeTo')).toBe('/decouverte')
      expect(header.prop('shouldBackFromDetails')).toBe(false)
    })

    it('should display a form element with an input text when component is mounted', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const form = wrapper.find('form')
      expect(form).toHaveLength(1)
      const textInput = form.find('input')
      expect(textInput).toHaveLength(1)
      expect(textInput.prop('name')).toBe('keywords')
      expect(textInput.prop('placeholder')).toBe('Saisir un mot-clé')
      expect(textInput.prop('type')).toBe('text')
    })

    it('should display a form element with a submit button when component is mounted', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const form = wrapper.find('form')
      const submitButton = form.find('button')
      expect(submitButton).toHaveLength(1)
      expect(submitButton.prop('type')).toBe('submit')
      expect(submitButton.text()).toBe('Chercher')
    })

    it('should not have results container when componenent is mounted', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const result = wrapper.find(ResultsContainer)
      expect(result).toHaveLength(0)
    })

    it('should not display waiting spinner when componenent is mounted', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const spinner = wrapper.find(Spinner)
      expect(spinner).toHaveLength(0)
    })

    it('should display a menu in the footer', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const footer = wrapper.find(RelativeFooterContainer)
      expect(footer).toHaveLength(1)
      expect(footer.prop('className')).toBe('dotted-top-red')
      expect(footer.prop('theme')).toBe('white')
    })
  })

  describe('when searching', () => {
    beforeEach(() => {
      fetch.mockReset()
    })

    it('should not trigger search request when no keywords', () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: null
          }
        },
        preventDefault: jest.fn()
      })

       // then
       expect(fetch).not.toHaveBeenCalledWith()
    })

    it('should trigger search request when keywords have been provided', () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')
      fetch.mockReturnValue({
        hits: [],
        nbHits: 0,
      })
      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: 'un livre très cherché'
          }
        },
        preventDefault: jest.fn()
      })

       // then
       expect(fetch).toHaveBeenCalledWith('un livre très cherché')
    })

    it('should display search keywords and number of results when 0 result', () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')
      fetch.mockReturnValue({
        hits: [],
        page: 0,
        nbHits: 0,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: "librairie",
        params: "query=librairie&hitsPerPage=2"
      })

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: 'librairie'
          }
        },
        preventDefault: jest.fn()
      })

      // then
      const resultTitle = wrapper.findWhere(node => node.text() === '"librairie" : 0 résultat').first()
      expect(resultTitle).toHaveLength(1)
    })

    it('should display search keywords and number of results when 2 results', async () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')
      fetch.mockReturnValue({
        hits: [{
            objectID: 'A8'
          },
          {
            objectID: 'A8'
          }
        ],
        page: 0,
        nbHits: 2,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: "librairie",
        params: "query=librairie&hitsPerPage=2"
      })

      // when
      await form.simulate('submit', {
        target: {
          keywords: {
            value: 'librairie'
          }
        },
        preventDefault: jest.fn()
      })

      // then
      const resultTitle = wrapper.findWhere(node => node.text() === '"librairie" : 2 résultats').first()
      expect(resultTitle).toHaveLength(1)
    })

    it('should not have results container when 0 result', () => {
      // given
      fetch.mockReturnValue({
        hits: [],
        page: 0,
        nbHits: 0,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: "",
        params: "query=&hitsPerPage=2"
      })
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: ''
          },
        },
        preventDefault: jest.fn()
      })

      // then
      const result = wrapper.find(ResultsContainer)
      expect(result).toHaveLength(0)
    })

    it('should have results container when search is over and find at least 1 result', () => {
      // given
      fetch.mockReturnValue({
        hits: [{
            objectID: 'A8'
          },
        ],
        page: 0,
        nbHits: 2,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: "librairie",
        params: "query='librairie'&hitsPerPage=2"
      })
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: 'librairie'
          },
        },
        preventDefault: jest.fn()
      })

      // then
      const results = wrapper.find(ResultsContainer)
      expect(results).toHaveLength(1)
    })

    it('should display an header with the right properties when there are results', () => {
      // given
      fetch.mockReturnValue({
        hits: [{
            objectID: 'A8'
          },
        ],
        page: 0,
        nbHits: 2,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: "librairie",
        params: "query='librairie'&hitsPerPage=2"
      })
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: 'librairie'
          },
        },
        preventDefault: jest.fn()
      })

      // then
      const header = wrapper.find(HeaderContainer)
      expect(header).toHaveLength(1)
      expect(header.prop('backTo')).toBe('/recherche-algolia')
      expect(header.prop('closeTitle')).toBe('Retourner à la page recherche')
      expect(header.prop('closeTo')).toBe('/recherche-algolia')
      expect(header.prop('shouldBackFromDetails')).toBe(false)
      expect(header.prop('title')).toBe('Recherche')
    })

    it('should display waiting spinner when it is searching', () => {
      // given
      fetch.mockReturnValue({
        hits: [{
            objectID: 'A8'
          },
        ],
        page: 0,
        nbHits: 2,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: "librairie",
        params: "query='librairie'&hitsPerPage=2"
      })
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: 'Ma recherche'
          }
        },
        preventDefault: jest.fn()
      })

      // then
      const spinner = wrapper.find(Spinner)
      expect(spinner).toHaveLength(1)
      expect(spinner.prop('label')).toBe('Recherche en cours')
    })

    it('should not display waiting spinner when results are fetched', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const spinner = wrapper.find(Spinner)
      expect(spinner).toHaveLength(0)
    })
  })

  describe('on detail page', () => {
    const buildStore = configureStore([thunk])
    let history
    let store
    const state = {
      data: {
        bookings: [],
        favorites: [],
        features: [],
        users: [{
          wallet_balance: 125,
        }],
        offers: [
          {
            id: 'A9',
            product: {
              thumbCount: 1,
              thumbUrl: ''
            }
          }
        ],
        mediations: [],
        recommendations: [],
        stocks: [],
      },
      geolocation: {
        latitude: 42.2,
        longitude: 2.2,
      },
    }

    beforeEach(() => {
      history = createMemoryHistory()
      store = buildStore(state)
    })

    it('should display an header with the right properties when on detail page', () => {
      // given
      history.push('/recherche-algolia/details/A9')
      const props = {
        match: {
          params: {
            details: "details"
          }
        }
      }

      // when
      const wrapper = mount(
        <Router history={history}>
          <Provider store={store} >
            <SearchAlgolia  {...props}/>
          </Provider>
        </Router>
      )

      // then
      const header = wrapper.find(HeaderContainer)
      expect(header).toHaveLength(1)
      expect(header.prop('title')).toBe('Recherche')
      expect(header.prop('backTo')).toBe(null)
      expect(header.prop('closeTitle')).toBe('Retourner à la page recherche')
      expect(header.prop('closeTo')).toBe('/recherche-algolia')
      expect(header.prop('shouldBackFromDetails')).toBe(true)
    })
  })

  describe('navigating on routes', () => {
    const buildStore = configureStore([thunk])
    let history
    let store
    const state = {
      data: {
        bookings: [],
        favorites: [],
        features: [],
        users: [{
          wallet_balance: 125,
        }],
        offers: [
          {
            id: 'A9',
            product: {
              thumbCount: 1,
              thumbUrl: ''
            }
          }
        ],
        mediations: [],
        recommendations: [],
        stocks: [],
      },
      geolocation: {
        latitude: 42.2,
        longitude: 2.2,
      },
    }

    beforeEach(() => {
      history = createMemoryHistory()
      store = buildStore(state)
    })

    it('should render search-algolia main page ', () => {
      // given
      history.push('/recherche-algolia')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Provider store={store}>
            <SearchAlgolia {...props} />
          </Provider>
        </Router>
      )

      // then
      const searchMainPage = wrapper.find('.search-container')
      const searchDetails = wrapper.find(SearchAlgoliaDetailsContainer)
      expect(searchMainPage).toHaveLength(1)
      expect(searchDetails).toHaveLength(0)
    })

    it('should render details page ', () => {
      // given
      history.push('/recherche-algolia/details/A9')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Provider store={store}>
            <SearchAlgolia {...props} />
          </Provider>
        </Router>
      )

      // then
      const searchMainPage = wrapper.find('.search-container')
      const searchDetails = wrapper.find(SearchAlgoliaDetailsContainer)
      expect(searchMainPage).toHaveLength(0)
      expect(searchDetails).toHaveLength(1)
    })
  })
})
