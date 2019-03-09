import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'

import {
  configureTestStore,
  configureFetchCurrentUserWithLoginFail,
} from './configure'
import { OnMountCaller } from './OnMountCaller'
import { withRedirectToSigninWhenNotAuthenticated } from '../withRedirectToSigninWhenNotAuthenticated'

const Test = () => null
const RedirectToSigninWhenNotAuthenticatedTest = withRedirectToSigninWhenNotAuthenticated(
  Test
)

describe('src | components | pages | hocs | with-login | withRedirectToSigninWhenNotAuthenticated', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<RedirectToSigninWhenNotAuthenticatedTest />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('functions', () => {
    it('should redirect to signin when not authenticated', done => {
      // given
      const history = createBrowserHistory()
      history.push('/test')
      const store = configureTestStore()
      configureFetchCurrentUserWithLoginFail()

      // when
      mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/test">
                <RedirectToSigninWhenNotAuthenticatedTest />
              </Route>
              <Route path="/connexion">
                <OnMountCaller onMountCallback={done} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )
    })
  })
})
