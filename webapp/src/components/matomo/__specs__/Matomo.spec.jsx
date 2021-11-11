import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import { getStubStore } from '../../../utils/stubStore'
import MatomoContainer from '../MatomoContainer'
import trackPageView from '../../../tracking/trackPageView'

jest.mock('../../../utils/config', () => ({
  MATOMO_GEOLOCATION_GOAL_ID: 1,
  ANDROID_APPLICATION_ID: 'app.passculture.testing.webapp',
}))

jest.mock('../../../tracking/trackPageView')

const flushPromises = () => new Promise(setImmediate)

describe('src | components | Matomo', () => {
  let fakeMatomo
  let history
  let store
  let props

  beforeEach(() => {
    history = createBrowserHistory()
    history.push('/router/path')
    fakeMatomo = {
      push: jest.fn(),
    }
    window._paq = fakeMatomo
    store = getStubStore({
      currentUser: (state = null) => state,
    })
  })

  afterEach(() => {
    trackPageView.mockClear()
  })

  it('should push a new page displayed event on direct access', async () => {
    // when
    mountMatomo(props, history, store)
    await flushPromises()

    // then
    expect(trackPageView).toHaveBeenCalledTimes(1)
    expect(fakeMatomo.push).toHaveBeenCalledTimes(4)
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(1, ['setCustomUrl', '/router/path'])
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(2, ['setDocumentTitle', ''])
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'ANONYMOUS on WEBAPP'])
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(4, [
      'setCustomVariable',
      1,
      'platform',
      'browser',
      'visit',
    ])
  })

  it('should track page view once only on URL change', async () => {
    // given
    mountMatomo(props, history, store)
    await flushPromises()

    // then
    expect(trackPageView).toHaveBeenCalledTimes(1)
    expect(fakeMatomo.push).toHaveBeenCalledTimes(4)
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(1, ['setCustomUrl', '/router/path'])

    // when
    history.push(`/connexion`)
    await flushPromises()

    // then
    expect(trackPageView).toHaveBeenCalledTimes(2)
    expect(fakeMatomo.push).toHaveBeenCalledTimes(9)
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(5, ['setCustomUrl', '/connexion'])
  })

  it('should push the page title', async () => {
    // given
    document.title = 'pass Culture page title'

    // when
    mountMatomo(props, history, store)
    await flushPromises()

    // then
    expect(trackPageView).toHaveBeenCalledTimes(1)
    expect(fakeMatomo.push).toHaveBeenCalledTimes(4)
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(1, ['setCustomUrl', '/router/path'])
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(2, [
      'setDocumentTitle',
      'pass Culture page title',
    ])
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'ANONYMOUS on WEBAPP'])
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(4, [
      'setCustomVariable',
      1,
      'platform',
      'browser',
      'visit',
    ])
  })

  describe('when user is not logged', () => {
    it('should push Anonymous as userId', async () => {
      // when
      mountMatomo(props, history, store)
      await flushPromises()

      // then
      expect(trackPageView).toHaveBeenCalledTimes(1)
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'ANONYMOUS on WEBAPP'])
    })

    it('should reset userId', async () => {
      // given
      history.push(`/connexion`)

      // when
      mountMatomo(props, history, store)
      await flushPromises()

      // then
      expect(trackPageView).toHaveBeenCalledTimes(1)
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(5, ['resetUserId'])
    })
  })

  describe('when user is logged', () => {
    it('should dispatch the user id when current user is logged', async () => {
      // given
      store = getStubStore({
        currentUser: (
          state = {
            id: '5FYTbfk4TR',
          }
        ) => state,
      })

      // when
      mountMatomo(props, history, store)
      await flushPromises()

      // then
      expect(trackPageView).toHaveBeenCalledTimes(1)
      expect(fakeMatomo.push).toHaveBeenCalledTimes(4)
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(1, ['setCustomUrl', '/router/path'])
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(2, [
        'setDocumentTitle',
        'pass Culture page title',
      ])
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', '5FYTbfk4TR on WEBAPP'])
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(4, [
        'setCustomVariable',
        1,
        'platform',
        'browser',
        'visit',
      ])
    })
  })

  describe('when user is coming from webapp', () => {
    it('should dispatch user id with the right platform and custom variable', async () => {
      // Given
      store = getStubStore({
        currentUser: (
          state = {
            id: '5FYTbfk4TR',
          }
        ) => state,
      })

      // When
      mountMatomo(props, history, store)
      await flushPromises()

      // Then
      expect(trackPageView).toHaveBeenCalledTimes(1)
      expect(fakeMatomo.push).toHaveBeenCalledWith(['setUserId', '5FYTbfk4TR on WEBAPP'])
      expect(fakeMatomo.push).toHaveBeenCalledWith([
        'setCustomVariable',
        1,
        'platform',
        'browser',
        'visit',
      ])
      expect(fakeMatomo.push).not.toHaveBeenCalledWith(['setUserId', '5FYTbfk4TR on TWA'])
      expect(fakeMatomo.push).not.toHaveBeenCalledWith([
        'setCustomVariable',
        1,
        'platform',
        'application',
        'visit',
      ])
    })
  })

  describe('when user is coming from twa', () => {
    it('should dispatch user id with the right platform and custom variable', async () => {
      // Given
      Object.defineProperty(document, 'referrer', {
        get: () => 'android-app://app.passculture.testing.webapp',
      })

      store = getStubStore({
        currentUser: (
          state = {
            id: '5FYTbfk4TR',
          }
        ) => state,
      })

      // When
      mountMatomo(props, history, store)
      await flushPromises()

      // Then
      expect(trackPageView).toHaveBeenCalledTimes(1)
      expect(fakeMatomo.push).toHaveBeenCalledWith(['setUserId', '5FYTbfk4TR on TWA'])
      expect(fakeMatomo.push).toHaveBeenCalledWith([
        'setCustomVariable',
        1,
        'platform',
        'application',
        'visit',
      ])
      expect(fakeMatomo.push).not.toHaveBeenCalledWith(['setUserId', '5FYTbfk4TR on WEBAPP'])
      expect(fakeMatomo.push).not.toHaveBeenCalledWith([
        'setCustomVariable',
        1,
        'platform',
        'browser',
        'visit',
      ])
    })
  })
})

function mountMatomo(props, history, store) {
  mount(
    <Router history={history}>
      <Provider store={store}>
        <MatomoContainer {...props} />
      </Provider>
    </Router>
  )
}
