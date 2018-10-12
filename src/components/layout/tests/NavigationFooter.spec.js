import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import NavigationFooter from '../NavigationFooter'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | NavigationFooter', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {}
      const store = mockStore(initialState)
      const props = {
        dispatch: jest.fn(),
        theme: 'fakeTheme',
      }

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <NavigationFooter {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
