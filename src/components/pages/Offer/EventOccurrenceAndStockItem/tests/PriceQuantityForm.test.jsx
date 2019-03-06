import React from 'react'
import { shallow } from 'enzyme'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'

import PriceQuantityForm from '../PriceQuantityForm'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | Offer | EventOccurrenceAndStockItem | PriceQuantityForm', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {}
      const store = mockStore(initialState)
      const initialProps = {}

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <PriceQuantityForm {...initialProps} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
