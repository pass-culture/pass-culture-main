import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'

import {
  configureFetchCurrentUserWithLoginSuccess,
  configureTestStore,
} from './configure'
import { OnMountCaller } from './OnMountCaller'
import { withRedirectToDiscoveryWhenAlreadyAuthenticated } from '../withRedirectToDiscoveryWhenAlreadyAuthenticated'

const Test = () => null
const RedirectToDiscoveryWhenAlreadyAuthenticatedTest = withRedirectToDiscoveryWhenAlreadyAuthenticated(
  Test
)

describe('src | components | pages | hocs | with-login | withRedirectToDiscoveryWhenAlreadyAuthenticated', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(
        <RedirectToDiscoveryWhenAlreadyAuthenticatedTest />
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('functions', () => {
    it('should redirect to discovery when already authenticated', done => {
      // given
      const history = createBrowserHistory()
      history.push('/test')
      const store = configureTestStore()
      configureFetchCurrentUserWithLoginSuccess()

      // when
      mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/test">
                <RedirectToDiscoveryWhenAlreadyAuthenticatedTest />
              </Route>
              <Route path="/decouverte">
                <OnMountCaller onMountCallback={done} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )
    })
  })
})
