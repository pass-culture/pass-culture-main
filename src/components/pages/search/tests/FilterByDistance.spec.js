import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import FilterByDistance from '../FilterByDistance'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | search | FilterByDistance', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {}
      const store = mockStore(initialState)
      const props = {
        filter: {},
        geolocation: {},
        title: 'Fake title',
      }

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <FilterByDistance {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
