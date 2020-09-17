import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import { getStubStore } from '../../../../utils/stubStore'
import LoadingPage from '../../../layout/LoadingPage/LoadingPage'
import withLogin from '../withLogin'

jest.mock('../../../../utils/fetch-normalize-data/requestData', () => ({
  ...jest.requireActual('/../../../../utils/fetch-normalize-data/requestData'),
  requestData: () => {
    return { type: 'REQUEST_DATA' }
  },
}))

describe('src | components | withLogin', () => {
  describe('when just has been mounted', () => {
    it('should display the loading page', () => {
      // given
      const store = getStubStore({
        data: (
          state = {
            features: [],
          }
        ) => state,
      })
      let dispatch = jest.fn()
      const wrappedComponent = () => (
        <h1>
          {'Hello World !'}
        </h1>
      )
      const config = {}
      const history = createBrowserHistory()

      // when
      const WithLoginComponent = withLogin(config)(wrappedComponent)
      const wrapper = mount(
        <Provider store={store}>
          <Router history={history}>
            <WithLoginComponent dispatch={dispatch} />
          </Router>
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
