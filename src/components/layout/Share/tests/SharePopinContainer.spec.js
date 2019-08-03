import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import SharePopinContainer from '../SharePopinContainer'

const middlewares = []
const mockStore = configureStore(middlewares)

const dispatchMock = jest.fn()

describe('src | components | share | SharePopinContainer', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {}
      const store = mockStore(initialState)
      const props = {
        dispatch: dispatchMock,
        options: true,
        visible: true,
      }
      // when
      const wrapper = shallow(
        <Provider store={store}>
          <SharePopinContainer {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
