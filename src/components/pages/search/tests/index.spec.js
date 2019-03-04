import { Provider } from 'react-redux'
import React from 'react'
import configureStore from 'redux-mock-store'
import { shallow } from 'enzyme'

import REDUX_STATE from '../../../../mocks/reduxState'

import Search from '../index'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | Search', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = REDUX_STATE
      const store = mockStore(initialState)

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <Search />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
