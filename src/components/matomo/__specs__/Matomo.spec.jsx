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
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'ANONYMOUS'])
    })
  })

  describe('when user is logged', () => {
    it('should dispatch tech or biz user id when user email contains teams domain', () => {
      // given
      store = mockStore({ user: { id: 'TY', email: 'fake@octo.com' } })

      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'TECH or BIZ USER'])
    })

    it('should dispatch pro user id when user when email is not one reserved', () => {
      // given
      store = mockStore({ user: { id: 'TY', email: 'fake@fake.com' } })

      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'PRO USER'])
    })

    it('should dispatch sandbox user id when user email contains sandbox domain', () => {
      // given
      store = mockStore({ user: { id: 'TY', email: 'fake@youpi.com' } })

      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer user={null} />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'SANDBOX USER'])
    })
  })
})
