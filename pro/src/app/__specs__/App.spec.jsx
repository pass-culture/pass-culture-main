import { setUser } from '@sentry/browser'
import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Route } from 'react-router'

import { URL_FOR_MAINTENANCE } from 'utils/config'
import { renderWithProviders } from 'utils/renderWithProviders'

import { App } from '../App'

jest.mock('hooks/useAnalytics', () => ({
  useConfigureFirebase: jest.fn(),
}))

jest.mock('hooks/useLogNavigation', () => jest.fn())

const renderApp = ({ props, store: storeOverrides, initialEntries = '/' }) =>
  renderWithProviders(
    <App {...props}>
      <Route path={'/'}>
        <p>Sub component</p>
      </Route>
      <Route path={'/login'}>
        <p>Login page</p>
      </Route>
      <Route path={'/offres'}>
        <p>Private Page</p>
      </Route>
    </App>,
    { storeOverrides, initialRouterEntries: [initialEntries] }
  )

jest.mock('@sentry/browser', () => ({
  setUser: jest.fn(),
}))

jest.spyOn(window, 'scrollTo').mockImplementation()

delete window.location
window.location = {}
const setHrefSpy = jest.fn()
Object.defineProperty(window.location, 'href', {
  set: setHrefSpy,
})

describe('src | App', () => {
  let props
  let store
  let user

  beforeEach(() => {
    user = {
      id: 'user_id',
      publicName: 'François',
      isAdmin: false,
    }
    store = {
      user: { initialized: true, currentUser: user },
    }
    props = {}
  })

  it('should render App and children components when isMaintenanceActivated is false', async () => {
    renderApp({ props, store })

    expect(await screen.findByText('Sub component')).toBeInTheDocument()
    expect(setUser).toHaveBeenCalledWith({ id: user.id })
  })

  it('should render a Redirect component when isMaintenanceActivated is true', async () => {
    store = {
      ...store,
      maintenance: {
        isActivated: true,
      },
    }
    renderApp({ props, store })

    await waitFor(() => {
      expect(setHrefSpy).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
    })
  })

  it('should render a Redirect component when route is private and user not logged in', () => {
    store = {
      ...store,
      user: { initialized: false, currentUser: null },
    }
    renderApp({ props, store, initialEntries: '/offres' })

    expect(screen.getByText('Sub component')).toBeInTheDocument()
  })

  it('should render a Redirect component when loging out', () => {
    store = {
      ...store,
      user: { initialized: false, currentUser: null },
    }
    renderApp({ props, store, initialEntries: '/logout' })

    expect(screen.getByText('Sub component')).toBeInTheDocument()
  })
})
