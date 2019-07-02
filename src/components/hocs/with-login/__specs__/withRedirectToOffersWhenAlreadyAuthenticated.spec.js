import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'

import {
  configureFetchCurrentUserWithLoginSuccess,
  configureFetchCurrentUserWithLoginSuccessAndOffers,
  configureTestStore,
} from './configure'
import { OnMountCaller } from './OnMountCaller'
import { withRedirectToOffersWhenAlreadyAuthenticated } from '../withRedirectToOffersWhenAlreadyAuthenticated'

const Test = () => null
const RedirectToOffersWhenAlreadyAuthenticatedTest = withRedirectToOffersWhenAlreadyAuthenticated(
  Test
)

describe('src | components | pages | hocs | with-login | withRedirectToOffersWhenAlreadyAuthenticated', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<RedirectToOffersWhenAlreadyAuthenticatedTest />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('functions', () => {
    it('should redirect to structures when when pro already authenticated but without offers', done => {
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
                <RedirectToOffersWhenAlreadyAuthenticatedTest />
              </Route>
              <Route path="/structures">
                <OnMountCaller onMountCallback={done} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )
    })

    it('should redirect to offers when pro already authenticated with offers and venue', done => {
      // given
      const history = createBrowserHistory()
      history.push('/test')
      const store = configureTestStore()
      configureFetchCurrentUserWithLoginSuccessAndOffers()

      // when
      mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/test">
                <RedirectToOffersWhenAlreadyAuthenticatedTest />
              </Route>
              <Route path="/offres">
                <OnMountCaller onMountCallback={done} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )
    })
  })
})
