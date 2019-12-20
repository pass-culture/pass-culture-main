import { createMemoryHistory } from 'history'
import { mount, shallow } from 'enzyme'
import { Provider } from 'react-redux'
import React from 'react'
import { Router } from 'react-router-dom'
import thunk from 'redux-thunk'

import configureStore from 'redux-mock-store'

import HeaderContainer from '../../../layout/Header/HeaderContainer'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import SearchAlgolia from '../SearchAlgolia'
import SearchAlgoliaDetailsContainer from '../Result/ResultDetail/ResultDetailContainer'
import Spinner from '../../../layout/Spinner/Spinner'
import { fetch } from '../service/algoliaService'
import state from '../../../../mocks/state'
import Result from '../Result/Result'

jest.mock('../service/algoliaService', () => ({
  fetch: jest.fn()
}))

describe('components | SearchAlgolia', () => {
  let props
  let change
  let clear
  let parse

  beforeEach(() => {
    fetch.mockReset()
    change = jest.fn()
    clear = jest.fn()
    parse = jest.fn().mockReturnValue({})
    props = {
      geolocation: {
        latitude: 40.1,
        longitude: 41.1
      },
      location: {
        pathname: '/',
        search: ''
      },
      query: {
        change,
        clear,
        parse
      }
    }
  })

  describe('when render', () => {
    it('should display a header with the right properties', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const header = wrapper.find(HeaderContainer)
      expect(header).toHaveLength(1)
    })

    it('should display a form element with an input text', () => {
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

    it('should display a form element with a submit button', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const form = wrapper.find('form')
      const submitButton = form.find('button')
      expect(submitButton).toHaveLength(1)
      expect(submitButton.prop('type')).toBe('submit')
      expect(submitButton.text()).toBe('Chercher')
    })

    it('should not display results when no keywords in url', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const results = wrapper.find(Result)
      expect(results).toHaveLength(0)
    })

    it('should not display waiting spinner', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const spinner = wrapper.find(Spinner)
      expect(spinner).toHaveLength(0)
    })

    it('should display a footer', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const footer = wrapper.find(RelativeFooterContainer)
      expect(footer).toHaveLength(1)
      expect(footer.prop('className')).toBe('dotted-top-red')
      expect(footer.prop('theme')).toBe('white')
    })

    describe('when keywords in url', () => {
      it('should fill search input, display keywords, number of results', () => {
        // given
        fetch.mockReturnValue({
          hits: [],
          nbHits: 0,
          page: 0
        })
        parse.mockReturnValue({
          'mots-cles': 'une librairie',
          page: 0
        })

        // when
        const wrapper = shallow(<SearchAlgolia {...props} />)

        // then
        const results = wrapper.find(Result)
        const searchInput = wrapper.find('input')
        const resultTitle = wrapper.findWhere(node => node.text() === '"une librairie" : 0 résultat').first()
        expect(results).toHaveLength(0)
        expect(searchInput.prop('defaultValue')).toBe('une librairie')
        expect(resultTitle).toHaveLength(1)
        expect(props.query.change).toHaveBeenCalledWith({ 'mots-cles': 'une librairie', page: 1 })
      })

      it('should fill search input and display keywords, number of results when results are found', () => {
        // given
        fetch.mockReturnValue({
          hits: [{}, {}],
          nbHits: 2,
          page: 0
        })
        parse.mockReturnValue({
          'mots-cles': 'une librairie'
        })

        // when
        const wrapper = shallow(<SearchAlgolia {...props} />)

        // then
        const results = wrapper.find(Result)
        const searchInput = wrapper.find('input')
        const resultTitle = wrapper.findWhere(node => node.text() === '"une librairie" : 2 résultats').first()
        expect(results).toHaveLength(2)
        expect(searchInput.prop('defaultValue')).toBe('une librairie')
        expect(resultTitle).toHaveLength(1)
      })

      describe('when no page query param', () => {
        it('should set page query param to 1', () => {
          // given
          fetch.mockReturnValue({
            hits: [],
            nbHits: 0,
            page: 0
          })
          parse.mockReturnValue({
            'mots-cles': 'une librairie'
          })

          // when
          shallow(<SearchAlgolia {...props} />)

          // then
          expect(props.query.change).toHaveBeenCalledWith({ 'mots-cles': 'une librairie', page: 1 })
        })
      })

      describe('when page query param is provided', () => {
        it('should fetch data using page query param value minus 1 when value is positive', () => {
          // given
          fetch.mockReturnValue({
            hits: [{}, {}],
            nbHits: 2,
            page: 0
          })
          parse.mockReturnValue({
            'mots-cles': 'une librairie',
            'page': 1
          })

          // when
          shallow(<SearchAlgolia {...props} />)

          // then
          expect(fetch).toHaveBeenCalledWith('une librairie', 0)
        })

        it('should fetch data using page 0 when page query param value is negative', () => {
          // given
          fetch.mockReturnValue({
            hits: [{}, {}],
            nbHits: 2,
            page: 0
          })
          parse.mockReturnValue({
            'mots-cles': 'une librairie',
            'page': -1
          })

          // when
          shallow(<SearchAlgolia {...props} />)

          // then
          expect(fetch).toHaveBeenCalledWith('une librairie', 0)
        })

        it('should fetch data using page 0 when page query param value is not a valid value', () => {
          // given
          fetch.mockReturnValue({
            hits: [{}, {}],
            nbHits: 2,
            page: 0
          })
          parse.mockReturnValue({
            'mots-cles': 'une librairie',
            'page': 'invalid value'
          })

          // when
          shallow(<SearchAlgolia {...props} />)

          // then
          expect(fetch).toHaveBeenCalledWith('une librairie', 0)
        })
      })
    })

    describe('when no keywords in url', () => {
      it('should clear all query params', () => {
        // given
        fetch.mockReturnValue({
          hits: [{}, {}],
          nbHits: 2,
          page: 0
        })
        parse.mockReturnValue({
          'page': 1
        })

        // when
        shallow(<SearchAlgolia {...props} />)

        // then
        expect(fetch).not.toHaveBeenCalledWith()
        expect(clear).toHaveBeenCalledWith()
      })
    })
  })

  describe('when searching', () => {
    it('should not trigger search request when no keywords', () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')

      // when
      form.simulate('submit', {
        target: {
          keywords: {
            value: ''
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
      expect(fetch).toHaveBeenCalledWith('un livre très cherché', 0)
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
        query: 'librairie',
        params: 'query=librairie&hitsPerPage=2'
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
        hits: [{}, {}],
        page: 0,
        nbHits: 2,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: 'librairie',
        params: 'query=librairie&hitsPerPage=2'
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

    it('should not display results when no results', () => {
      // given
      fetch.mockReturnValue({
        hits: [],
        page: 0,
        nbHits: 0,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: '',
        params: 'query=&hitsPerPage=2'
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
      const results = wrapper.find(Result)
      expect(results).toHaveLength(0)
    })

    it('should display results when search succeeded with at least one result', () => {
      // given
      const offer = { objectId: 'AE', offer: { name: 'Livre de folie' } }
      fetch.mockReturnValue({
        hits: [offer],
        page: 0,
        nbHits: 1,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: 'librairie',
        params: 'query=\'librairie\'&hitsPerPage=2'
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
      const results = wrapper.find(Result)
      expect(results).toHaveLength(1)
      expect(results.at(0).prop('result')).toStrictEqual(offer)
      expect(results.at(0).prop('geolocation')).toStrictEqual({ latitude: 40.1, longitude: 41.1 })
    })

    it('should add query params in url when fetching data', () => {
      // given
      const offer = { objectId: 'AE', offer: { name: 'Livre de folie' } }
      fetch.mockReturnValue({
        hits: [offer],
        page: 0,
        nbHits: 1,
        nbPages: 0,
        hitsPerPage: 2,
        processingTimeMS: 1,
        query: 'librairie',
        params: 'query=\'librairie\'&hitsPerPage=2'
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
      expect(props.query.change).toHaveBeenCalledWith({ 'mots-cles': 'librairie', 'page': 1 })
    })
  })

  describe('when navigating', () => {
    let history
    let store
    const buildStore = configureStore([thunk])

    beforeEach(() => {
      history = createMemoryHistory()
      store = buildStore(state)
    })

    it('should render search main page when current route is /recherche-algolia', () => {
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
      const form = wrapper.find('form')
      const searchDetails = wrapper.find(SearchAlgoliaDetailsContainer)
      expect(form).toHaveLength(1)
      expect(searchDetails).toHaveLength(0)
    })

    it('should render item details when current route is /recherche-algolia/details/AE', () => {
      // given
      history.push('/recherche-algolia/details/AE')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Provider store={store}>
            <SearchAlgolia {...props} />
          </Provider>
        </Router>
      )

      // then
      const form = wrapper.find('form')
      const searchDetails = wrapper.find(SearchAlgoliaDetailsContainer)
      expect(form).toHaveLength(0)
      expect(searchDetails).toHaveLength(1)
    })
  })
})
