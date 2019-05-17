import { mount } from 'enzyme'
import React from 'react'
import { createBrowserHistory } from 'history'
import { Router } from 'react-router'
import MatomoPageTracker from '../MatomoPageTracker'

describe('src | components | hocs | MatomoPageTracker', () => {
  let history
  beforeEach(() => {
    history = createBrowserHistory()
    history.push('/router/path')
  })

  it('should dispatch a new page displayed event', () => {
    // given
    const fakeMatomoPageTracker = {
      push: jest.fn(),
    }
    // eslint-disable-next-line
    window._paq = fakeMatomoPageTracker

    // when
    mount(
      <Router history={history}>
        <MatomoPageTracker />
      </Router>
    )

    // then
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(1, [
      'setCustomUrl',
      '/router/path',
    ])
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(3, ['trackPageView'])
  })

  it('should dispatch the page title', () => {
    // given
    const fakeMatomoPageTracker = {
      push: jest.fn(),
    }
    // eslint-disable-next-line
    window._paq = fakeMatomoPageTracker
    document.title = 'PassCulture Page Name'

    // when
    mount(
      <Router history={history}>
        <MatomoPageTracker />
      </Router>
    )

    // then
    expect(fakeMatomoPageTracker.push).toHaveBeenNthCalledWith(2, [
      'setDocumentTitle',
      'PassCulture Page Name',
    ])
  })
})
