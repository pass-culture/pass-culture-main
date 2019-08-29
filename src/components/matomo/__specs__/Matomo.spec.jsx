import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import MatomoContainer from '../MatomoContainer'

describe('src | components | matomo | Matomo', () => {
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
    mount(
      <Router history={history}>
        <MatomoContainer />
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
        <MatomoContainer />
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
          <MatomoContainer />
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
          <MatomoContainer />
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
          <MatomoContainer />
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
})
