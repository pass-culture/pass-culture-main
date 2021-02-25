import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import MatomoContainer from '../MatomoContainer'

const renderMatomo = (history, storeData = {}) => {
  const store = configureTestStore(storeData)

  return mount(
    <Provider store={store}>
      <Router history={history}>
        <MatomoContainer />
      </Router>
    </Provider>
  )
}

describe('src | components | Matomo', () => {
  let fakeMatomo
  let history

  beforeEach(() => {
    history = createBrowserHistory()
    history.push('/router/path')

    fakeMatomo = {
      push: jest.fn(),
    }
    window._paq = fakeMatomo
  })

  it('should push a new page displayed event', () => {
    // when
    renderMatomo(history)

    // then
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(1, ['setCustomUrl', '/router/path'])
  })

  it('should push the page title', () => {
    // given
    document.title = 'pass Culture page title'

    // when
    renderMatomo(history)

    // then
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(2, [
      'setDocumentTitle',
      'pass Culture page title',
    ])
  })

  describe('when user is not logged', () => {
    it('should push Anonymous as userId', () => {
      // when
      renderMatomo(history)

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'ANONYMOUS on PRO'])
    })

    it('should reset userId', () => {
      // given
      history.push(`/connexion`)

      // when
      renderMatomo(history)

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(4, ['resetUserId'])
    })
  })

  describe('when user is logged', () => {
    it('should dispatch setUserId with current user id', () => {
      // given
      const store = {
        data: {
          users: [{ id: 'TY' }],
        },
      }

      // when
      renderMatomo(history, store)

      // then
      expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['setUserId', 'TY on PRO'])
    })
  })
})
