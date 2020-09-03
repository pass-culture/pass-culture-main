import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import { getStubStore } from '../../../utils/stubStore'
import MatomoContainer from '../MatomoContainer'

describe('src | components | Matomo', () => {
  let fakeMatomo
  let history
  let store

  beforeEach(() => {
    history = createBrowserHistory()
    history.push('/router/path')

    fakeMatomo = {
      push: jest.fn(),
    }
    window._paq = fakeMatomo
    store = getStubStore({
      data: (state = {}) => state,
    })
  })

  it('should push a new page displayed event', () => {
    // when
    mount(
      <Router history={history}>
        <Provider store={store}>
          <MatomoContainer />
        </Provider>
      </Router>
    )

    // then
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(1, ['setCustomUrl', '/router/path'])
  })

  it('should push the page title', () => {
    // given
    document.title = 'pass Culture page title'

    // when
    mount(
      <Router history={history}>
        <Provider store={store}>
          <MatomoContainer />
        </Provider>
      </Router>
    )

    // then
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(2, [
      'setDocumentTitle',
      'pass Culture page title',
    ])
  })

  describe('when user is not logged', () => {
    it('should push Anonymous as userId', () => {
      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'ANONYMOUS on PRO'])
    })

    it('should reset userId', () => {
      // given
      history.push(`/connexion`)

      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(4, ['resetUserId'])
    })
  })

  describe('when user is logged', () => {
    it('should dispatch setUserId with current user id', () => {
      // given
      const store = getStubStore({
        data: (
          state = {
            users: [
              {
                id: 'TY',
              },
            ],
          }
        ) => state,
      })

      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'TY on PRO'])
    })
  })
})
