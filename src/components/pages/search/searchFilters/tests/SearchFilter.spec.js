import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { mount, shallow } from 'enzyme'
import { Route, Router } from 'react-router-dom'
import configureStore from 'redux-mock-store'

import SearchFilter from '../SearchFilter'
import SearchFilterContainer from '../SearchFilterContainer'
import { INITIAL_FILTER_PARAMS } from '../../utils'
import REDUX_STATE from '../../../../../mocks/reduxState'

const dispatchMock = jest.fn()
const queryChangeMock = jest.fn()
const queryClearMock = jest.fn()

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | search | SearchFilter', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        isVisible: true,
        location: {},
        query: {
          parse: jest.fn(),
        },
        resetSearchStore: jest.fn(),
      }

      // when
      const wrapper = shallow(<SearchFilter {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('functions', () => {
    describe('constructor', () => {
      it('should initialize state with current query arguments', () => {
        // given
        const mockedObject = { prop: 'mocked object' }
        const mockQueryParse = jest.fn(() => mockedObject)
        const props = {
          isVisible: false,
          location: {},
          query: {
            parse: mockQueryParse,
          },
          resetSearchStore: jest.fn(),
        }

        // when
        const wrapper = shallow(<SearchFilter {...props} />)
        expect(wrapper.instance().state.params).toStrictEqual(mockedObject)
      })
    })

    describe('onComponentDidUpdate', () => {
      it('should update state if params has changed', () => {
        // given
        const initialState = REDUX_STATE
        const store = mockStore(initialState)
        const history = createBrowserHistory()
        history.push('/test?categories=Jouer')

        // when
        const wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <Route path="/test">
                <SearchFilterContainer isVisible />
              </Route>
            </Router>
          </Provider>
        )
        history.push('/test?categories=Sourire')

        // then
        const searchFilter = wrapper.find('SearchFilter')
        const updatedQuery = searchFilter.state('params')
        const filterParamsMatchingQueryParamsKey = searchFilter.state(
          'filterParamsMatchingQueryParams'
        )
        const expected = {
          categories: 'Sourire',
        }
        expect(updatedQuery).toEqual(expected)
        expect(filterParamsMatchingQueryParamsKey).toEqual(false)
      })
    })

    describe('onResetClick', () => {
      it('should call the hoc withQueryRouter query.change method with INITIAL_FILTER_PARAMS', () => {
        // given
        const props = {
          dispatch: dispatchMock,
          isVisible: true,
          location: { search: '?page=1&jours=0-1' },
          query: {
            change: queryChangeMock,
            parse: () => ({
              categories: 'Lire, Regarder',
              distance: 50,
              jours: '0-1',
              page: '1',
            }),
          },
          resetSearchStore: jest.fn(),
        }
        const wrapper = shallow(
          <SearchFilterContainer.WrappedComponent.WrappedComponent {...props} />
        )

        // when
        wrapper.instance().onResetClick()
        const updatedFormState = wrapper.state()
        const expected = {
          filterParamsMatchingQueryParams: false,
          initialDateParams: true,
          params: {
            date: null,
            distance: null,
            jours: null,
          },
        }

        expect(updatedFormState).toEqual(expected)

        expect(queryChangeMock).toHaveBeenCalledWith(INITIAL_FILTER_PARAMS, {
          pathname: '/recherche/resultats',
        })
      })
    })

    describe('onFilterClick', () => {
      it('should call hoc withQueryRouter change method with the good parameters', () => {
        // given
        const mockResetSearchStore = jest.fn()
        const props = {
          dispatch: dispatchMock,
          isVisible: true,
          location: { search: '?page=1&jours=0-1' },
          query: {
            change: queryChangeMock,
            clear: queryClearMock,
            parse: () => ({
              jours: '0-1',
              page: '1',
            }),
          },
          resetSearchStore: mockResetSearchStore,
        }

        // when
        const wrapper = shallow(
          <SearchFilterContainer.WrappedComponent.WrappedComponent {...props} />
        )
        wrapper.instance().onFilterClick()
        const currentQuery = wrapper.state('params')
        const updatedFormState = wrapper.state(
          'filterParamsMatchingQueryParams'
        )

        // THEN
        expect(updatedFormState).toEqual(false)
        expect(mockResetSearchStore).not.toHaveBeenCalled()
        expect(queryChangeMock).toHaveBeenCalledWith(currentQuery, {
          pathname: '/recherche/resultats',
        })
      })
    })
  })
})
