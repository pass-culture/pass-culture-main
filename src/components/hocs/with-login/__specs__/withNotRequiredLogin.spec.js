import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'

import { configureTestStore } from './configure'
import { OnMountCaller } from './OnMountCaller'
import withNotRequiredLogin, { handleSuccess } from '../withNotRequiredLogin'
import { getRedirectToCurrentLocationOrDiscovery } from '../helpers'

jest.mock('../helpers')

const Test = () => null
const NotRequiredLoginTest = withNotRequiredLogin(Test)

describe('src | components | pages | hocs | with-login | withNotRequiredLogin', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<NotRequiredLoginTest />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('functions', () => {
    it('should redirect to discovery when already authenticated and needsToFillCulturalSurvey', () => {
      return new Promise(done => {
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
                  <NotRequiredLoginTest />
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

    it('should redirect to currentLocation when already authenticated and not needsToFillCulturalSurvey', () => {
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
                <NotRequiredLoginTest />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )

      expect(history.location.pathname).toBe('/test')
    })
  })

  describe('handleSuccess()', () => {
    it('should call getRedirectToCurrentLocationOrDiscovery with right parameters', () => {
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
      expect(getRedirectToCurrentLocationOrDiscovery).toHaveBeenCalledWith({
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
      getRedirectToCurrentLocationOrDiscovery.mockReturnValue('/fake-url')

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
      getRedirectToCurrentLocationOrDiscovery.mockReturnValue(undefined)

      // when
      handleSuccess(state, action, ownProps)

      // then
      expect(ownProps.history.push).not.toBeCalled()
    })
  })
})
