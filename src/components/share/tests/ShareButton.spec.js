import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import { ShareButton } from '../ShareButton'

const middlewares = []
const mockStore = configureStore(middlewares)

const dispatchMock = jest.fn()

describe('src | components | share | ShareButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {
        options: {},
        user: {
          email: 'fake@email.fr',
        },
        visible: true,
      }
      const store = mockStore(initialState)
      const props = {
        dispatch: dispatchMock,
      }
      // when
      const wrapper = shallow(
        <Provider store={store}>
          <ShareButton {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
