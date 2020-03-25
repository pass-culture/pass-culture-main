import withLogin from '../withLogin'
import { mount } from 'enzyme'

import React from 'react'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import LoadingPage from '../../../layout/LoadingPage/LoadingPage'

jest.mock('redux-thunk-data', () => ({
  ...jest.requireActual('redux-thunk-data'),
  requestData: () => {
    return { type: 'REQUEST_DATA' }
  },
}))

describe('src | components | pages | hocs | with-login | withLogin', () => {
  describe('when just has been mounted', () => {
    it('should display the loading page', () => {
      // given
      const initialState = { data: { users: [] } }
      const middlewares = []
      const mockStore = configureStore(middlewares)
      const store = mockStore(initialState)
      let handleFail = jest.fn()
      let handleSuccess = jest.fn()
      let dispatch = jest.fn()
      const wrappedComponent = () => (<h1>
        {'Hello World !'}
      </h1>)
      const config = {
        handleFail,
        handleSuccess,
      }

      // when
      const WithLoginComponent = withLogin(config)(wrappedComponent)
      const wrapper = mount(
        <Provider store={store}>
          <WithLoginComponent dispatch={dispatch} />
        </Provider>
      )

      // then
      const loadingPage = wrapper.find(LoadingPage)
      expect(loadingPage.exists()).toBe(true)
      const wrappedComponentInHOC = wrapper.findWhere(htmlElement =>
        htmlElement.text().includes('Hello World !')
      )
      expect(wrappedComponentInHOC.exists()).toBe(false)
    })
  })
})
