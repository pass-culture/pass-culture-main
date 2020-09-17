import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'

import {
  configureTestStore,
  configureFetchCurrentUserWithLoginFail,
} from './configure'
import OnMountCaller from './OnMountCaller'
import withRequiredLogin from '../withRequiredLogin'

const Test = () => null
const RequiredLoginTest = withRequiredLogin(Test)

describe('src | components | pages | hocs | with-login | withRequiredLogin', () => {
  afterEach(() => {
    fetch.resetMocks()
  })

  describe('functions', () => {
    it('should redirect to signin when not authenticated', async() => {await new Promise((resolve, reject) => {
      // given
      const history = createBrowserHistory()
      history.push('/test')
      const store = configureTestStore()
      configureFetchCurrentUserWithLoginFail()
      function onSuccessMountCallback() {
        expect(history.location.pathname).toStrictEqual("/connexion")
        resolve()
      }

      // when
      mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/test">
                <RequiredLoginTest />
              </Route>
              <Route path="/connexion">
                <OnMountCaller onMountCallback={onSuccessMountCallback} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )

      setTimeout(() => reject('Should have been redirected to /connexion'))
    })})
  })
})
