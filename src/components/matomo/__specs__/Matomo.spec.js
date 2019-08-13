import { mount } from 'enzyme'
import React from 'react'
import { createBrowserHistory } from 'history'
import { Router } from 'react-router'
import Matomo from '../Matomo'

describe('src | components | Matomo', () => {
  let history
  beforeEach(() => {
    history = createBrowserHistory()
    history.push('/router/path')
  })

  it('should dispatch a new page displayed event', () => {
    // given
    const fakeMatomo = {
      push: jest.fn(),
    }
    window._paq = fakeMatomo

    // when
    mount(
      <Router history={history}>
        <Matomo />
      </Router>
    )

    // then
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(1, ['setCustomUrl', '/router/path'])
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(3, ['trackPageView'])
  })

  it('should dispatch the page title', () => {
    // given
    const fakeMatomo = {
      push: jest.fn(),
    }
    window._paq = fakeMatomo
    document.title = 'PassCulture Page Name'

    // when
    mount(
      <Router history={history}>
        <Matomo />
      </Router>
    )

    // then
    expect(fakeMatomo.push).toHaveBeenNthCalledWith(2, [
      'setDocumentTitle',
      'PassCulture Page Name',
    ])
  })
})
