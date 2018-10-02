import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import FilterByOfferTypes from '../FilterByOfferTypes'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | search | FilterByOfferTypes', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {}
      const store = mockStore(initialState)
      const props = {
        filter: {},
        title: 'Fake title',
        typeSublabels: [],
      }

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <FilterByOfferTypes {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
