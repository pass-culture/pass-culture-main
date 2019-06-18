import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'

import { configureTestStore } from './configure'
import { OnMountCaller } from './OnMountCaller'
import withRequiredLogin from '../withRequiredLogin'

const Test = () => null
const RequiredLoginTest = withRequiredLogin(Test)

describe('src | components | pages | hocs | with-login | withRequiredLogin', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<RequiredLoginTest />)

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
      fetch.mockResponse(
        JSON.stringify([{ global: ['Nobody is authenticated here'] }]),
        { status: 400 }
      )

      // when
      mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/test">
                <RequiredLoginTest />
              </Route>
              <Route path="/connexion">
                <OnMountCaller onMountCallback={done} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )
    })
    it('should redirect to typeform when authenticated and not needsToFillCulturalSurvey', done => {
      // given
      const history = createBrowserHistory()
      history.push('/test')
      const store = configureTestStore()
      fetch.mockResponse(
        JSON.stringify({
          email: 'michel.marx@youpi.fr',
          needsToFillCulturalSurvey: true,
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
                <RequiredLoginTest />
              </Route>
              <Route path="/typeform">
                <OnMountCaller onMountCallback={done} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )
    })

    it('should not redirect when authenticated and needsToFillCulturalSurvey', () => {
      // given
      const history = createBrowserHistory()
      history.push('/test')
      const store = configureTestStore()
      fetch.mockResponse(
        JSON.stringify({
          email: 'michel.marx@youpi.fr',
          needsToFillCulturalSurvey: false,
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
                <RequiredLoginTest />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )

      expect(history.location.pathname).toBe('/test')
    })
  })
})
