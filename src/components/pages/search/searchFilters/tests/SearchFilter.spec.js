import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router } from 'react-router-dom'
import { Transition } from 'react-transition-group'
import configureStore from 'redux-mock-store'

import FilterByDates from '../../FilterByDates'
import FilterByDistanceContainer from '../../FilterByDistanceContainer'
import FilterByOfferTypesContainer from '../../FilterByOfferTypesContainer'
import SearchFilter from '../SearchFilter'
import SearchFilterContainer from '../SearchFilterContainer'
import { INITIAL_FILTER_PARAMS } from '../../utils'
import REDUX_STATE from '../../../../../mocks/reduxState'

describe('src | components | pages | search | searchFilters | SearchFilter', () => {
  let props

  beforeEach(() => {
    props = {
      isVisible: true,
      location: {},
      onClickFilterButton: jest.fn(),
      query: {
        change: jest.fn(),
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

  describe('constructor()', () => {
    it('should initialize state with current query arguments', () => {
      // given
      const queryParams = { prop: 'mocked object' }
      jest.spyOn(props.query, 'parse').mockImplementation(() => queryParams)
      const wrapper = shallow(<SearchFilter {...props} />)

      // when
      const { params } = wrapper.instance().state

      // then
      expect(params).toStrictEqual(queryParams)
    })
  })

  describe('onComponentDidUpdate', () => {
    it('should reinitialize the state if the URL has changed', () => {
      // given
      const mockOnClickFilterButton = jest.fn()
      const store = configureStore([])(REDUX_STATE)
      const history = createBrowserHistory()
      history.push('/test?categories=Jouer')
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

      // when
      history.push('/test?categories=Sourire')

      // then
      const params = wrapper.find('SearchFilter').state()
      expect(params).toStrictEqual({
        filterParamsMatchingQueryParams: false,
        initialDateParams: true,
        params: {
          categories: 'Sourire',
        },
      })
    })
  })

  describe('onClickFilterButton()', () => {
    it('should close the filters and change the URL by default', () => {
      // given
      const wrapper = shallow(<SearchFilter {...props} />)

      // when
      wrapper.instance().onClickFilterButton()

      // then
      expect(props.onClickFilterButton).toHaveBeenCalledWith(props.isVisible)
    })

    it('should reset the store when filter params match the query params', () => {
      // given
      const wrapper = shallow(<SearchFilter {...props} />)
      wrapper.setState({ filterParamsMatchingQueryParams: true })

      // when
      wrapper.instance().onClickFilterButton()

      // then
      expect(props.resetSearchStore).toHaveBeenCalled()
    })
  })

  describe('onClickReset()', () => {
    it('should initialize default filter params and reset the URL', () => {
      // given
      const wrapper = shallow(<SearchFilter {...props} />)

      // when
      wrapper.instance().onClickReset()

      // then
      const expected = {
        filterParamsMatchingQueryParams: false,
        initialDateParams: true,
        params: {},
      }
      expect(props.resetSearchStore).toHaveBeenCalled()
      expect(wrapper.state()).toStrictEqual(expected)
      expect(props.query.change).toHaveBeenCalledWith(INITIAL_FILTER_PARAMS, {
        pathname: '/recherche/resultats',
      })
    })
  })

  describe('handleQueryAdd()', () => {
    it('should add filter parameters when I have not initial parameters', () => {
      // given
      props.query.parse = () => ({})
      const wrapper = shallow(<SearchFilter {...props} />)

      // when
      wrapper.instance().handleQueryAdd('jours', '0-1', jest.fn())

      // then
      expect(wrapper.state()).toStrictEqual({
        filterParamsMatchingQueryParams: 'jours',
        initialDateParams: true,
        params: {
          jours: '0-1',
        },
      })
    })

    it('should add filter parameters when I have initial parameters', () => {
      // given
      props.query.parse = () => ({
        categories: 'Jouer',
      })
      const wrapper = shallow(<SearchFilter {...props} />)

      // when
      wrapper.instance().handleQueryAdd('categories', 'Lire', undefined)

      // then
      expect(wrapper.state()).toStrictEqual({
        filterParamsMatchingQueryParams: 'categories',
        initialDateParams: true,
        params: {
          categories: 'Jouer,Lire',
        },
      })
    })
  })

  describe('handleQueryRemove()', () => {
    it('should remove filter parameters when I have initial parameters', () => {
      // given
      props.query.parse = () => ({
        categories: 'Jouer,Applaudir',
      })
      const wrapper = shallow(<SearchFilter {...props} />)

      // when
      wrapper.instance().handleQueryRemove('categories', 'Jouer', undefined)

      // then
      expect(wrapper.state()).toStrictEqual({
        filterParamsMatchingQueryParams: 'categories',
        initialDateParams: true,
        params: {
          categories: 'Applaudir',
        },
      })
    })
  })

  describe('render()', () => {
    it('should have three filters and one reset button and one filter button by default', () => {
      // given
      const store = configureStore([])(REDUX_STATE)
      const wrapper = mount(
        <Provider store={store}>
          <SearchFilter {...props} />
        </Provider>
      )

      // when
      const transition = wrapper.find(Transition)
      const filterByDates = transition.find(FilterByDates)
      const filterByDistanceContainer = transition.find(
        FilterByDistanceContainer
      )
      const filterByOfferTypesContainer = transition.find(
        FilterByOfferTypesContainer
      )
      const resetButton = transition.find('#search-filter-reset-button')
      const filterButton = transition.find('#filter-button')

      // then
      expect(transition).toHaveLength(1)
      expect(filterByDates).toHaveLength(1)
      expect(filterByDistanceContainer).toHaveLength(1)
      expect(filterByOfferTypesContainer).toHaveLength(1)
      expect(resetButton).toHaveLength(1)
      expect(filterButton).toHaveLength(1)
    })
  })
})
