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
import withNotRequiredLogin from '../withNotRequiredLogin'

const Test = () => null
const NotRequiredLogin = withNotRequiredLogin(Test)

describe('src | components | pages | hocs | with-login | withNotRequiredLogin', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<NotRequiredLogin />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('functions', () => {
    it('should redirect to offerers when already authenticated and not hasOffers', done => {
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
                <NotRequiredLogin />
              </Route>
              <Route path="/structures">
                <OnMountCaller onMountCallback={done} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )
    })

    it('should redirect to offers when already authenticated and hasOffers', done => {
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
                <NotRequiredLogin />
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
