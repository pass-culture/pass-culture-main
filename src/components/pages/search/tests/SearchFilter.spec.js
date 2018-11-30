import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { mount, shallow } from 'enzyme'
import { Route, Router } from 'react-router-dom'
import configureStore from 'redux-mock-store'

import SearchFilter from '../SearchFilter'
import { INITIAL_FILTER_PARAMS } from '../utils'
import REDUX_STATE from '../../../../mocks/reduxState'

const dispatchMock = jest.fn()
const queryChangeMock = jest.fn()

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | search | SearchFilter', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        isVisible: true,
        query: {
          params: {
            categories: null,
            date: '2018-09-28T12:52:52.341Z',
            distance: '50',
            jours: '0-1',
            latitude: '48.8637546',
            longitude: '2.337428',
            [`mots-cles`]: 'fake',
            orderBy: 'offer.id+desc',
          },
        },
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
      it.skip('should initilize state with functions', () => {
        // given
        const props = {
          isVisible: false,
          params: {
            params: {},
          },
        }

        // when
        const wrapper = shallow(<SearchFilter {...props} />)
        wrapper.instance().handleQueryAdd = jest.fn()
        wrapper.instance().handleQueryChange = jest.fn()
        wrapper.instance().handleQueryRemove = jest.fn()

        // then
        expect(wrapper.state().add).toEqual('mocked function handleQueryAdd ')
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
                <SearchFilter isVisible />
              </Route>
            </Router>
          </Provider>
        )
        history.push('/test?categories=Sourire')

        // then
        const searchFilter = wrapper.find('SearchFilter')
        const updatedQuery = searchFilter.state('params')
        const isNewKey = searchFilter.state('isNew')
        const expected = {
          categories: 'Sourire',
        }
        expect(updatedQuery).toEqual(expected)
        expect(isNewKey).toEqual(false)
      })
    })

    describe('onResetClick', () => {
      it('should call hoc withQueryRouter change method with the good parameters', () => {
        // given
        const props = {
          dispatch: dispatchMock,
          isVisible: true,
          location: { search: '?page=1&jours=0-1' },
          query: {
            change: queryChangeMock,
            params: {
              jours: '0-1',
              page: '1',
            },
          },
        }

        // when
        const wrapper = shallow(
          <SearchFilter.WrappedComponent.WrappedComponent {...props} />
        )
        wrapper.instance().onResetClick()
        const updatedFormState = wrapper.state('isNew')

        expect(updatedFormState).toEqual('jours')

        expect(queryChangeMock).toHaveBeenCalledWith(INITIAL_FILTER_PARAMS, {
          pathname: '/recherche/resultats',
        })
      })
    })

    describe('onFilterClick', () => {
      it('should call hoc pagination change method with the good parameters', () => {
        // given
        const props = {
          dispatch: dispatchMock,
          isVisible: true,
          location: { search: '?page=1&jours=0-1' },
          query: {
            change: queryChangeMock,
            params: {
              jours: '0-1',
              page: '1',
            },
          },
        }

        // when
        const wrapper = shallow(
          <SearchFilter.WrappedComponent.WrappedComponent {...props} />
        )
        wrapper.instance().onFilterClick()
        const currentQuery = wrapper.state('params')
        const updatedFormState = wrapper.state('isNew')

        // THEN
        expect(queryChangeMock).toHaveBeenCalledWith(currentQuery, {
          pathname: '/recherche/resultats',
        })

        expect(updatedFormState).toEqual(false)
      })
    })
  })
})
