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
  let props

  const mockStore = configureMockStore()

  beforeEach(() => {
    history = createBrowserHistory()
    history.push('/router/path')
    props = {tracking: {trackEvent: jest.fn()}}

    fakeMatomo = {
      push: jest.fn(),
    }
    window._paq = fakeMatomo
    initialState = {
      data: {
        users: [],
      },
      geolocation: {
        latitude: null,
        longitude: null,
      },
    }
    store = mockStore(initialState)
  })

  it('should track user geolocation when user is geolocated', () => {
    // given
    store = mockStore({
      data: {
        users: [
          {
            id: 'a1',
          },
        ],
      },
      geolocation: {
        latitude: 1,
        longitude: 1,
      },
    })
    // when
    mount(
      <Router history={history}>
        <Provider store={store}>
          <MatomoContainer {...props} />
        </Provider>
      </Router>
    )

    // then
    expect(props.tracking.trackEvent).toHaveBeenNthCalledWith(1, { action: 'activatedGeolocation', name: 'a1' })
  })

  it('should not track user geolocation when user is not geolocated', () => {
    // given
    store = mockStore({
      data: {
        users: [
          {
            id: 'a1',
          },
        ],
      },
      geolocation: {
        latitude: null,
        longitude: null,
      },
    })
    // when
    mount(
      <Router history={history}>
        <Provider store={store}>
          <MatomoContainer {...props} />
        </Provider>
      </Router>
    )

    // then
    expect(props.tracking.trackEvent).not.toHaveBeenCalledWith()
  })

  it('should push a new page displayed event', () => {
    // when
    mount(
      <Router history={history}>
        <Provider store={store}>
          <MatomoContainer {...props} />
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
          <MatomoContainer {...props} />
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
            <MatomoContainer {...props} />
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
            <MatomoContainer {...props} />
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
            <MatomoContainer {...props} />
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
    it('should push Anonymous as userId', () => {
      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer {...props} />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'ANONYMOUS on WEBAPP'])
    })

    it('should reset userId', () => {
      // given
      history.push(`/connexion`)

      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer {...props} />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(4, ['resetUserId'])
    })
  })

  describe('when user is logged', () => {
    it('should dispatch the user id when current user is logged', () => {
      // given
      store = mockStore({
        data: {
          users: [
            {
              id: '5FYTbfk4TR',
            },
          ],
        },
        geolocation: {
          latitude: null,
          longitude: null,
        },
      })

      // when
      mount(
        <Router history={history}>
          <Provider store={store}>
            <MatomoContainer {...props} />
          </Provider>
        </Router>
      )

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', '5FYTbfk4TR on WEBAPP'])
    })
  })
})
