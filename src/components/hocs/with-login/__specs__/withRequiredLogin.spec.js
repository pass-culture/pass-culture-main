import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'

import { configureTestStore } from './configure'
import { OnMountCaller } from './OnMountCaller'
import withRequiredLogin, {
  handleFail,
  handleSuccess,
} from '../withRequiredLogin'
import {
  getRedirectToSignin,
  getRedirectToCurrentLocationOrTypeform,
} from '../helpers'

const Test = () => null
const RequiredLoginTest = withRequiredLogin(Test)

jest.mock('../helpers')

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
    it('should redirect to signin when not authenticated', () => {
      return new Promise(done => {
        // given
        const history = createBrowserHistory()
        history.push('/test')
        const store = configureTestStore()
        fetch.mockResponse(JSON.stringify([{ global: ['Nobody is authenticated here'] }]), {
          status: 400,
        })

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

  describe('handleFail()', () => {
    it('should call push history when its fail', () => {
      // given
      const state = {}
      const action = {}
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToSignin.mockReturnValue('/fake-url')

      // when
      handleFail(state, action, ownProps)

      // then
      expect(ownProps.history.push).toHaveBeenCalledWith('/fake-url')
    })
  })

  describe('handleSuccess()', () => {
    it('should call getRedirectToCurrentLocationOrTypeform with right parameters', () => {
      // given
      const state = {}
      const action = {
        payload: {},
      }
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(getRedirectToCurrentLocationOrTypeform).toHaveBeenCalledWith({
        currentUser: {
          email: 'michel.marx@youpi.fr',
          needsToFillCulturalSurvey: false,
        },
        hash: '',
        key: expect.any(String),
        pathname: '/test',
        search: '',
        state: undefined,
      })
    })

    it('should not call push history when user is redirected', () => {
      // given
      const state = {}
      const action = {
        payload: {},
      }
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToCurrentLocationOrTypeform.mockReturnValue('/fake-url')

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(ownProps.history.push).toHaveBeenCalledWith('/fake-url')
    })

    it('should call push history when its success', () => {
      // given
      const state = {}
      const action = {
        payload: {},
      }
      const ownProps = {
        history: {
          push: jest.fn(),
        },
        location: {},
      }
      getRedirectToCurrentLocationOrTypeform.mockReturnValue(undefined)

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(ownProps.history.push).not.toBeCalled()
    })
  })
})
