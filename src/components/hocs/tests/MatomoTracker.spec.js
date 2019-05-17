import { mount } from 'enzyme'
import React from 'react'
import { createBrowserHistory } from 'history'
import { Router } from 'react-router'
import MatomoTracker from '../MatomoTracker'

describe('src | components | hocs | MatomoTracker', () => {
  let history
  beforeEach(() => {
    history = createBrowserHistory()
    history.push('/router/path')
  })

  it('should dispatch a new page displayed event', () => {
    // given
    const fakeMatomoTracker = {
      push: jest.fn(),
    }
    // eslint-disable-next-line
    window._paq = fakeMatomoTracker

    // when
    mount(
      <Router history={history}>
        <MatomoTracker />
      </Router>
    )

    // then
    expect(fakeMatomoTracker.push).toHaveBeenNthCalledWith(1, [
      'setCustomUrl',
      '/router/path',
    ])
    expect(fakeMatomoTracker.push).toHaveBeenNthCalledWith(3, ['trackPageView'])
  })

  it('should dispatch the page title', () => {
    // given
    const fakeMatomoTracker = {
      push: jest.fn(),
    }
    // eslint-disable-next-line
    window._paq = fakeMatomoTracker
    document.title = 'PassCulture Page Name'

    // when
    mount(
      <Router history={history}>
        <MatomoTracker />
      </Router>
    )

    // then
    expect(fakeMatomoTracker.push).toHaveBeenNthCalledWith(2, [
      'setDocumentTitle',
      'PassCulture Page Name',
    ])
  })
})
