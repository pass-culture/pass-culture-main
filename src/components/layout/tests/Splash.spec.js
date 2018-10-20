import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import Splash from '../Splash'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | layout | Splash', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      const initialState = {}
      const store = mockStore(initialState)
      const wrapper = shallow(
        <Provider store={store}>
          <Splash />
        </Provider>
      )
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
