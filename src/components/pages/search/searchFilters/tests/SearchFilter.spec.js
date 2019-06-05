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

const queryChangeMock = jest.fn()
const queryClearMock = jest.fn()

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | search | SearchFilter', () => {
  let props

  beforeEach(() => {
    props = {
      isVisible: true,
      location: {},
      onClickFilterButton: jest.fn(),
      query: {
        parse: jest.fn(),
      },
      resetSearchStore: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<SearchFilter {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('constructor', () => {
    it('should initialize state with current query arguments', () => {
      // given
      const mockedObject = { prop: 'mocked object' }
      const mockQueryParse = jest.fn(() => mockedObject)
      props.isVisible = false
      props.query.parse = mockQueryParse
      const wrapper = shallow(<SearchFilter {...props} />)

      // when
      const { params } = wrapper.instance().state

      // then
      expect(params).toStrictEqual(mockedObject)
    })
  })

  describe('onComponentDidUpdate', () => {
    it('should update state if params has changed', () => {
      // given
      const mockOnClickFilterButton = jest.fn()
      const initialState = REDUX_STATE
      const store = mockStore(initialState)
      const history = createBrowserHistory()
      history.push('/test?categories=Jouer')

      // when
      const wrapper = mount(
        <Provider store={store}>
          <Router history={history}>
            <Route path="/test">
              <SearchFilterContainer
                isVisible
                onClickFilterButton={mockOnClickFilterButton}
              />
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
    it('should initialize default filter params when clicking on reset button', () => {
      // given
      props.location = { search: '?page=1&jours=0-1' }
      props.query = {
        change: queryChangeMock,
        parse: () => ({
          categories: 'Lire, Regarder',
          distance: 50,
          jours: '0-1',
          page: '1',
        }),
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

      // then
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
      props.location = { search: '?page=1&jours=0-1' }
      props.query = {
        change: queryChangeMock,
        clear: queryClearMock,
        parse: () => ({
          jours: '0-1',
          page: '1',
        }),
      }
      const wrapper = shallow(
        <SearchFilterContainer.WrappedComponent.WrappedComponent {...props} />
      )

      // when
      wrapper.instance().onClickFilterButton()
      const currentQuery = wrapper.state('params')
      const updatedFormState = wrapper.state('filterParamsMatchingQueryParams')

      // then
      expect(updatedFormState).toEqual(false)
      expect(mockResetSearchStore).not.toHaveBeenCalled()
      expect(queryChangeMock).toHaveBeenCalledWith(currentQuery, {
        pathname: '/recherche/resultats',
      })
    })
  })
})
