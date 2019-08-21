import configureMockStore from 'redux-mock-store'
import { createBrowserHistory } from 'history'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'

import React from 'react'
import { Router } from 'react-router'

import MatomoContainer from '../MatomoContainer'

describe('src | components | matomo | Matomo', () => {
  let fakeMatomo
  let history
  let initialState
  let store

  const mockStore = configureMockStore()

  beforeEach(() => {
    history = createBrowserHistory()
    history.push('/router/path')

    fakeMatomo = {
      push: jest.fn(),
    }
    window._paq = fakeMatomo
    initialState = { user: null }
    store = mockStore(initialState)
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
  it('should dispatch the user id when user is logged', () => {
    // given
    const fakeMatomoPageTracker = {
      push: jest.fn(),
    }
    window._paq = fakeMatomoPageTracker

    store = mockStore({ user: { id: 'TY' } })

    // when
    mount(
      <Router history={history}>
        <Provider store={store}>
          <MatomoContainer />
        </Provider>
      </Router>
    )

    // then
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(3, ['setUserId', 'TY'])
  })

  it('should dispatch Anonymous when user is not logged', () => {
    // given
    const fakeMatomoPageTracker = {
      push: jest.fn(),
    }
    window._paq = fakeMatomoPageTracker

    // when
    mount(
      <Router history={history}>
        <Provider store={store}>
          <MatomoContainer user={null} />
        </Provider>
      </Router>
    )

    // then
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(3, ['setUserId', 'Anonymous'])
  })
})
