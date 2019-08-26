import configureMockStore from 'redux-mock-store'
import { createBrowserHistory } from 'history'
import { getCurrentUserUUID } from 'with-react-redux-login'
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
    initialState = { data: { users: [] } }
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

  describe('when have no location.search', () => {
    it('should not track site search', () => {
      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).not.toHaveBeenNthCalledWith(3, ['trackSiteSearch'])
    })
  })

  describe('when have location.search and no categories', () => {
    it('should track site search', () => {
      // given
      history.location.search = '?mots-cles=MEFA'

      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['trackSiteSearch', 'MEFA', false, false])
    })
  })

  describe('when have location.search and categories', () => {
    it('should track site search', () => {
      // given
      history.location.search = '?categories=Applaudir&mots-cles=MEFA'

      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, [
        'trackSiteSearch',
        'MEFA',
        'Applaudir',
        false,
      ])
    })
  })

  describe('when user is not logged', () => {
    it('should push Anonymous and unknown type as userId', () => {
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
    it('should dispatch the correct user id when user is a beneficiary', () => {
      // given
      store = mockStore({
        data: {
          users: [
            {
              currentUserUUID: getCurrentUserUUID(),
              email: 'fake@fake.com',
              canBookFreeOffers: true,
            },
          ],
        },
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
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'BENEFICIARY on WEBAPP'])
    })

    it('should dispatch the correct user id when user email contains team domain even if canBookFreeOffers is set to true', () => {
      // given
      store = mockStore({
        data: {
          users: [
            {
              currentUserUUID: getCurrentUserUUID(),
              email: 'fake@octo.com',
              canBookFreeOffers: true,
            },
          ],
        },
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
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'TECH or BIZ on WEBAPP'])
    })

    it('should dispatch the correct user id when user email contains sandbox domain even if canBookFreeOffers is set to true', () => {
      // given
      store = mockStore({
        data: {
          users: [
            {
              currentUserUUID: getCurrentUserUUID(),
              email: 'fake@youpi.com',
              canBookFreeOffers: true,
            },
          ],
        },
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
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'SANDBOX USER on WEBAPP'])
    })
  })
})
