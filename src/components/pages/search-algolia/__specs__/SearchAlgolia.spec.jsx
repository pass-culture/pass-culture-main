import { createBrowserHistory, createMemoryHistory } from 'history'
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
import Result from '../Result/Result'

import { fetch } from '../service/algoliaService'
import state from '../../../../mocks/state'
import { toast } from 'react-toastify'

jest.mock('../service/algoliaService', () => ({
  fetch: jest.fn(),
}))
jest.mock('react-toastify', () => ({
  toast: {
    info: jest.fn(),
  },
}))

describe('components | SearchAlgolia', () => {
  let props
  let change
  let clear
  let parse

  beforeEach(() => {
    change = jest.fn()
    clear = jest.fn()
    parse = jest.fn().mockReturnValue({})
    props = {
      geolocation: {
        latitude: 40.1,
        longitude: 41.1,
      },
      location: {
        search: '',
      },
      match: {
        params: {},
      },
      query: {
        change,
        clear,
        parse,
      },
      redirectToSearchMainPage: jest.fn(),
    }
  })

  afterEach(() => {
    fetch.mockReset()
    parse.mockReset()
  })

  describe('when render', () => {
    it('should display a header with the right properties', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const header = wrapper.find(HeaderContainer)
      expect(header).toHaveLength(2)
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
      expect(textInput.prop('placeholder')).toBe('Artiste, auteur...')
      expect(textInput.prop('type')).toBe('text')
    })

    it('should display a form element with a submit button', () => {
      // when
      const wrapper = shallow(<SearchAlgolia {...props} />)

      // then
      const form = wrapper.find('form')
      const submitButton = form.findWhere(node => node.prop('type') === 'submit').first()
      expect(submitButton).toHaveLength(1)
      expect(submitButton.text()).toBe('Rechercher')
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
      expect(footer.prop('extraClassName')).toBe('dotted-top-red')
      expect(footer.prop('theme')).toBe('white')
    })

    describe('when keywords in url', () => {
      it('should fill search input, display keywords, number of results', async () => {
        // given
        fetch.mockReturnValue(
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
          page: 0,
        })

        // when
        const wrapper = await shallow(<SearchAlgolia {...props} />)

        // then
        const results = wrapper.find(Result)
        const searchInput = wrapper.find('input')
        const resultTitle = wrapper
          .findWhere(node => node.text() === '"une librairie" : 0 résultat')
          .first()
        expect(results).toHaveLength(0)
        expect(searchInput.prop('value')).toBe('une librairie')
        expect(resultTitle).toHaveLength(1)
        expect(props.query.change).toHaveBeenCalledWith({ 'mots-cles': 'une librairie', page: 1 })
      })

      it('should fill search input and display keywords, number of results when results are found', async () => {
        // given
        fetch.mockReturnValue(
          new Promise(resolve => {
            resolve({
              hits: [{ objectID: 'AA' }, { objectID: 'BB' }],
              nbHits: 2,
              page: 0,
            })
          })
        )
        parse.mockReturnValue({
          'mots-cles': 'une librairie',
        })

        // when
        const wrapper = await shallow(<SearchAlgolia {...props} />)

        // then
        const results = wrapper.find(Result)
        const searchInput = wrapper.find('input')
        const resultTitle = wrapper
          .findWhere(node => node.text() === '"une librairie" : 2 résultats')
          .first()
        expect(results).toHaveLength(2)
        expect(searchInput.prop('value')).toBe('une librairie')
        expect(resultTitle).toHaveLength(1)
      })

      describe('when no page query param', () => {
        it('should set page query param to 1', async () => {
          // given
          fetch.mockReturnValue(
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

          // when
          await shallow(<SearchAlgolia {...props} />)

          // then
          expect(props.query.change).toHaveBeenCalledWith({ 'mots-cles': 'une librairie', page: 1 })
        })
      })

      describe('when page query param is provided', () => {
        it('should fetch data using page query param value minus 1 when value is positive', () => {
          // given
          fetch.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [{ objectID: 'AA' }, { objectID: 'BB' }],
                nbHits: 2,
                page: 0,
              })
            })
          )
          parse.mockReturnValue({
            'mots-cles': 'une librairie',
            page: 1,
          })

          // when
          shallow(<SearchAlgolia {...props} />)

          // then
          expect(fetch).toHaveBeenCalledWith('une librairie', 0, '40.1, 41.1')
        })

        it('should fetch data using page 0 when page query param value is negative', async () => {
          // given
          fetch.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [{ objectID: 'AA' }, { objectID: 'BB' }],
                nbHits: 2,
                page: 0,
              })
            })
          )
          parse.mockReturnValue({
            'mots-cles': 'une librairie',
            page: -1,
          })

          // when
          await shallow(<SearchAlgolia {...props} />)

          // then
          expect(fetch).toHaveBeenCalledWith('une librairie', 0, '40.1, 41.1')
        })

        it('should fetch data using page 0 when page query param value is not a valid value', async () => {
          // given
          fetch.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [{ objectID: 'AA' }, { objectID: 'BB' }],
                nbHits: 2,
                page: 0,
              })
            })
          )
          parse.mockReturnValue({
            'mots-cles': 'une librairie',
            page: 'invalid value',
          })

          // when
          await shallow(<SearchAlgolia {...props} />)

          // then
          expect(fetch).toHaveBeenCalledWith('une librairie', 0, '40.1, 41.1')
        })
      })
    })

    describe('when no keywords in url', () => {
      it('should clear all query params', () => {
        // given
        fetch.mockReturnValue({
          hits: [{ objectID: 'AA' }, { objectID: 'BB' }],
          nbHits: 2,
          page: 0,
        })
        parse.mockReturnValue({
          page: 1,
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
            value: '',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      expect(fetch).not.toHaveBeenCalledWith()
    })

    it('should not trigger search request when keywords contains only spaces', () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)
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
      expect(fetch).not.toHaveBeenCalledWith()
    })

    it('should trigger search request when keywords have been provided', async () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')
      fetch.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [],
            nbHits: 0,
          })
        })
      )
      // when
      await form.simulate('submit', {
        target: {
          keywords: {
            value: 'un livre très cherché',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      expect(fetch).toHaveBeenCalledWith('un livre très cherché', 0, '40.1, 41.1')
    })

    it('should display search keywords and number of results when 0 result', async () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')
      fetch.mockReturnValue(
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
      const resultTitle = wrapper
        .findWhere(node => node.text() === '"librairie" : 0 résultat')
        .first()
      expect(resultTitle).toHaveLength(1)
    })

    it('should display search keywords and number of results when 2 results', async () => {
      // given
      const wrapper = shallow(<SearchAlgolia {...props} />)
      const form = wrapper.find('form')
      fetch.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [{ objectID: 'AA' }, { objectID: 'BB' }],
            page: 0,
            nbHits: 2,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'librairie',
            params: 'query=librairie&hitsPerPage=2',
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

      // then
      const resultTitle = wrapper
        .findWhere(node => node.text() === '"librairie" : 2 résultats')
        .first()
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
        params: 'query=&hitsPerPage=2',
      })
      const wrapper = shallow(<SearchAlgolia {...props} />)
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
      const results = wrapper.find(Result)
      expect(results).toHaveLength(0)
    })

    it('should display results when search succeeded with at least one result', async () => {
      // given
      const offer = { objectID: 'AE', offer: { name: 'Livre de folie' } }
      fetch.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [offer],
            page: 0,
            nbHits: 1,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'librairie',
            params: "query='librairie'&hitsPerPage=2",
          })
        })
      )
      const wrapper = shallow(<SearchAlgolia {...props} />)
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
      const results = wrapper.find(Result)
      expect(results).toHaveLength(1)
      expect(results.at(0).prop('geolocation')).toStrictEqual({ latitude: 40.1, longitude: 41.1 })
      expect(results.at(0).prop('result')).toStrictEqual(offer)
    })

    it('should add query params in url when fetching data', async () => {
      // given
      const offer = { objectID: 'AE', offer: { name: 'Livre de folie' } }
      fetch.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [offer],
            page: 0,
            nbHits: 1,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'librairie',
            params: "query='librairie'&hitsPerPage=2",
          })
        })
      )
      const wrapper = shallow(<SearchAlgolia {...props} />)
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
      expect(props.query.change).toHaveBeenCalledWith({ 'mots-cles': 'librairie', page: 1 })
    })

    it('should clear previous results and page number when searching with new keywords', async () => {
      // given
      const offer1 = { objectID: 'AE', offer: { name: 'Livre de folie' } }
      const offer2 = { objectID: 'AF', offer: { name: 'Livre bien' } }
      const offer3 = { objectID: 'AG', offer: { name: 'Livre nul' } }
      fetch.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [offer1, offer2],
            page: 0,
            nbHits: 1,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'librairie',
            params: "query='librairie'&hitsPerPage=2",
          })
        })
      )
      const wrapper = shallow(<SearchAlgolia {...props} />)
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
      const resultsFirstFetch = wrapper.find(Result)
      expect(resultsFirstFetch).toHaveLength(2)

      // when
      fetch.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [offer3],
            page: 0,
            nbHits: 1,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'vas-y',
            params: "query='vas-y'&hitsPerPage=2",
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

      // then
      const resultSecondFetch = wrapper.find(Result)
      expect(resultSecondFetch).toHaveLength(1)
      expect(wrapper.state()).toStrictEqual({
        currentPage: 0,
        hasSearchBeenMade: true,
        keywordsToSearch: 'vas-y',
        isLoading: false,
        results: [{ objectID: 'AG', offer: { name: 'Livre nul' } }],
        resultsCount: 1,
        searchedKeywords: 'vas-y',
        totalPagesNumber: 0,
      })
    })

    it('should not trigger a second search request when submitting same keywords twice', async () => {
      // given
      const offer1 = { objectID: 'AE', offer: { name: 'Livre de folie de la librairie' } }
      const offer2 = { objectID: 'AF', offer: { name: 'Livre bien de la librairie' } }
      fetch.mockReturnValue(
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
      const wrapper = shallow(<SearchAlgolia {...props} />)
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
      const resultsFirstFetch = wrapper.find(Result)
      expect(resultsFirstFetch).toHaveLength(2)

      // when
      fetch.mockReturnValue(
        new Promise(resolve => {
          resolve({
            hits: [offer1, offer2],
            page: 0,
            nbHits: 1,
            nbPages: 0,
            hitsPerPage: 2,
            processingTimeMS: 1,
            query: 'vas-y',
            params: 'query=librairie&hitsPerPage=2',
          })
        })
      )
      await form.simulate('submit', {
        target: {
          keywords: {
            value: 'librairie',
          },
        },
        preventDefault: jest.fn(),
      })

      // then
      const resultSecondFetch = wrapper.find(Result)
      expect(resultSecondFetch).toHaveLength(2)
    })

    it('should display an error when search failed', async () => {
      // given
      fetch.mockReturnValue(
        new Promise(reject => {
          reject()
        })
      )
      const wrapper = shallow(<SearchAlgolia {...props} />)
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
      await toast.info
      expect(toast.info).toHaveBeenCalledWith(
        "La recherche n'a pas pu aboutir, veuillez ré-essayer plus tard."
      )
    })

    describe('reset cross', () => {
      it('should not display reset cross when nothing is typed in text input', () => {
        // when
        const wrapper = shallow(<SearchAlgolia {...props} />)

        // then
        const resetButton = wrapper.findWhere(node => node.prop('type') === 'reset').first()
        expect(resetButton).toHaveLength(0)
      })

      it('should display reset cross when something is typed in text input', () => {
        // given
        const wrapper = shallow(<SearchAlgolia {...props} />)
        const form = wrapper.find('form')
        const input = form.find('input')

        // when
        input.simulate('change', {
          target: {
            name: 'keywords',
            value: 'typed search',
          },
          preventDefault: jest.fn(),
        })

        // then
        const resetButton = wrapper.findWhere(node => node.prop('type') === 'reset').first()
        expect(resetButton).toHaveLength(1)
      })

      it('should clear text input when clicking on reset cross', async () => {
        // given
        const history = createMemoryHistory()
        history.push('/recherche-offres?mots-cles=librairie&page=2')

        const wrapper = await mount(
          <Router history={history}>
            <SearchAlgolia {...props} />
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
        const resetButton = wrapper.findWhere(node => node.prop('type') === 'reset').first()

        // when
        resetButton.simulate('click')

        // then
        const expectedMissingResetButton = wrapper
          .findWhere(node => node.prop('type') === 'reset')
          .first()
        const resettedInput = form.find('input').first()
        expect(expectedMissingResetButton).toHaveLength(0)
        expect(resettedInput.instance().value).toBe('')
      })
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

    it('should render search main page when current route is /recherche-offres', () => {
      // given
      history.push('/recherche-offres')

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

    it('should render item details when current route is /recherche-offres/details/AE', () => {
      // given
      history.push('/recherche-offres/details/AE')

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

    describe('search icon and come back icon', () => {
      it('should display magnifying glass icon when current route is /recherche-offres', () => {
        // when
        const wrapper = shallow(<SearchAlgolia {...props} />)

        // then
        const form = wrapper.find('form')
        const magnifyingGlassIcon = form
          .findWhere(node => node.prop('svg') === 'picto-search')
          .first()
        expect(magnifyingGlassIcon).toHaveLength(1)
      })

      it('should render an icon to come back to search main page when a research has been made', async () => {
        // given
        fetch.mockReturnValue(
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
          page: 0,
        })

        // when
        const wrapper = await shallow(<SearchAlgolia {...props} />)

        // then
        console.log(wrapper.debug())
        const form = wrapper.find('form')
        const backIcon = form.findWhere(node => node.prop('svg') === 'picto-back-grey').first()
        expect(backIcon).toHaveLength(1)
      })

      it('should reset text input when clicking on come back arrow', async () => {
        // given
        fetch.mockReturnValue(
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
          page: 0,
        })
        const redirectToSearchMainPage = jest.fn()

        // when
        const wrapper = await shallow(
          <SearchAlgolia
            {...props}
            redirectToSearchMainPage={redirectToSearchMainPage}
          />
        )

        const form = wrapper.find('form')
        const backButton = form.findWhere(node => node.prop('type') === 'button').first()
        expect(wrapper.state('keywordsToSearch')).toBe('une librairie')
        backButton.simulate('click')

        // then
        expect(redirectToSearchMainPage).toHaveBeenCalledTimes(1)
        expect(wrapper.state('keywordsToSearch')).toBe('')
      })
    })

    describe('header', () => {
      it('should display a close button redirecting to discovery when arriving on search page', () => {
        // given
        const history = createBrowserHistory()
        history.push('/recherche-offres')
        props.match = {
          params: {},
        }

        // when
        const wrapper = mount(
          <Router history={history}>
            <SearchAlgolia {...props} />
          </Router>
        )

        // then
        const header = wrapper.find(HeaderContainer).first()
        expect(header.prop('closeTo')).toBe('/decouverte')
        expect(header.prop('closeTitle')).toBe('Retourner à la page découverte')
        expect(header.prop('shouldBackFromDetails')).toBe(false)
      })

      it('should not render header when search has been made', async () => {
        // given
        history.push('/recherche-offres?mots-cles=librairie&page=1')
        const offer1 = { objectID: 'AE', offer: { name: 'Livre de folie de la librairie' } }
        const offer2 = { objectID: 'AF', offer: { name: 'Livre bien de la librairie' } }
        fetch.mockReturnValue(
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
            <SearchAlgolia {...props} />
          </Router>
        )
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
        const header = wrapper.find(HeaderContainer)
        expect(header).toHaveLength(0)
      })

      it('should render header when on details page', () => {
        // given
        history.push('/recherche-offres/details/AE?mots-cles=librairie&page=1')

        // when
        const wrapper = mount(
          <Router history={history}>
            <Provider store={store}>
              <SearchAlgolia {...props} />
            </Provider>
          </Router>
        )

        // then
        const header = wrapper.find(HeaderContainer)
        expect(header).toHaveLength(1)
      })
    })
  })
})
