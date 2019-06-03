import { shallow } from 'enzyme'
import React from 'react'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'

import EditAndDeleteControl from '../EditAndDeleteControl'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | Offer | StockItem | EditAndDeleteControl', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {}
      const store = mockStore(initialState)
      const initialProps = {
        dispatch: jest.fn(),
      }

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <EditAndDeleteControl {...initialProps} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
