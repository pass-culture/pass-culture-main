import { setUser } from '@sentry/browser'
import { screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { URL_FOR_MAINTENANCE } from 'utils/config'
import { renderWithProviders } from 'utils/renderWithProviders'

import { App } from '../App'

vi.mock('hooks/useAnalytics', () => ({ useConfigureFirebase: vi.fn() }))
vi.mock('hooks/useLogNavigation', () => ({ default: vi.fn() }))
vi.mock('hooks/usePageTitle', () => ({ default: vi.fn() }))
vi.mock('@sentry/browser', () => ({ setUser: vi.fn() }))

const renderApp = (storeOverrides: any, url = '/') =>
  renderWithProviders(
    <>
      <div id="root"></div>

      <Routes>
        <Route path="/" element={<App />}>
          <Route path="/" element={<p>Sub component</p>} />
          <Route path="/connexion" element={<p>Login page</p>} />
        </Route>
      </Routes>
    </>,
    { storeOverrides, initialRouterEntries: [url] }
  )

global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value: {
    href: 'someurl',
  },
  writable: true,
})

describe('App', () => {
  let store: any

  beforeEach(() => {
    store = {
      user: {
        initialized: true,
        currentUser: {
          id: 12,
          isAdmin: false,
        },
      },
    }
    vi.spyOn(window, 'scrollTo')
  })

  it('should render App and children components when isMaintenanceActivated is false', async () => {
    renderApp(store)

    expect(await screen.findByText('Sub component')).toBeInTheDocument()
    expect(setUser).toHaveBeenCalledWith({
      id: store.user.currentUser.id.toString(),
    })
  })

  it('should render a Redirect component when isMaintenanceActivated is true', async () => {
    store = {
      ...store,
      maintenance: {
        isActivated: true,
      },
    }
    renderApp(store)

    await waitFor(() => {
      expect(window.location.href).toEqual(URL_FOR_MAINTENANCE)
    })
  })

  describe('cookies banner', () => {
    it('should render the cookie banner', async () => {
      renderApp(store)
      expect(
        await screen.findByText(
          /Nous utilisons des cookies et traceurs afin d’analyser l’utilisation de la plateforme et vous proposer la meilleure expérience possible/
        )
      ).toBeInTheDocument()
    })
  })
})
