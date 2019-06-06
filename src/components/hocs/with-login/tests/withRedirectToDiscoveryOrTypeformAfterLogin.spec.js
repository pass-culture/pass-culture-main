import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'

import { configureTestStore } from './configure'
import { OnMountCaller } from './OnMountCaller'
import withRedirectToDiscoveryOrTypeformAfterLogin from '../withRedirectToDiscoveryOrTypeformAfterLogin'

const Test = () => null
const RedirectToDiscoveryOrTypeformAfterLoginTest = withRedirectToDiscoveryOrTypeformAfterLogin(
  Test
)

describe('src | components | pages | hocs | with-login | withRedirectToDiscoveryOrTypeformAfterLogin', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<RedirectToDiscoveryOrTypeformAfterLoginTest />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('functions', () => {
    it('should redirect to discovery when already authenticated and hasFilledCulturalSurvey', done => {
      // given
      const history = createBrowserHistory()
      history.push('/test')
      const store = configureTestStore()
      fetch.mockResponse(
        JSON.stringify({
          email: 'michel.marx@youpi.fr',
          hasFilledCulturalSurvey: true,
        }),
        {
          status: 200,
        }
      )

      // when
      mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/test">
                <RedirectToDiscoveryOrTypeformAfterLoginTest />
              </Route>
              <Route path="/decouverte">
                <OnMountCaller onMountCallback={done} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )
    })
    it('should redirect to currentLocation when already authenticated and not hasFilledCulturalSurvey', () => {
      // given
      const history = createBrowserHistory()
      history.push('/test')
      const store = configureTestStore()
      fetch.mockResponse(
        JSON.stringify({
          email: 'michel.marx@youpi.fr',
          hasFilledCulturalSurvey: false,
        }),
        {
          status: 200,
        }
      )

      // when
      mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/test">
                <RedirectToDiscoveryOrTypeformAfterLoginTest />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )

      expect(history.location.pathname).toBe('/test')
    })
  })
})
