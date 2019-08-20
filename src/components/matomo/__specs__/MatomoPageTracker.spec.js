import { createBrowserHistory } from 'history'
import { mount } from 'enzyme'
import React from 'react'
import { Router } from 'react-router'

import MatomoPageTracker from '../MatomoPageTracker'

describe('src | components | matomo | MatomoPageTracker', () => {
  let history
  const props = {
    user: {
      id: 'TY',
    },
  }

  beforeEach(() => {
    history = createBrowserHistory()
    history.push('/router/path')
  })

  it('should dispatch a new page displayed event', () => {
    // given
    const fakeMatomoPageTracker = {
      push: jest.fn(),
    }
    window._paq = fakeMatomoPageTracker

    // when
    mount(
      <Router history={history}>
        <MatomoPageTracker {...props} />
      </Router>
    )

    // then
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(1, ['setCustomUrl', '/router/path'])
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(3, ['trackPageView'])
  })

  it('should dispatch the page title', () => {
    // given
    const fakeMatomoPageTracker = {
      push: jest.fn(),
    }
    window._paq = fakeMatomoPageTracker
    document.title = 'PassCulture Page Name'

    // when
    mount(
      <Router history={history}>
        <MatomoPageTracker {...props} />
      </Router>
    )

    // then
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(2, [
      'setDocumentTitle',
      'PassCulture Page Name',
    ])
  })

  it('should dispatch the user id when user is logged', () => {
    // given
    const fakeMatomoPageTracker = {
      push: jest.fn(),
    }
    window._paq = fakeMatomoPageTracker

    // when
    mount(
      <Router history={history}>
        <MatomoPageTracker {...props} />
      </Router>
    )

    // then
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(4, ['setUserId', 'TY'])
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
        <MatomoPageTracker user={null} />
      </Router>
    )

    // then
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(4, ['setUserId', 'Anonymous'])
  })
})
