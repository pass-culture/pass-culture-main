import { setUser } from '@sentry/browser'
import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import * as useAnalytics from 'hooks/useAnalytics'
import * as cookieConsentModal from 'utils/cookieConsentModal'
import { renderWithProviders } from 'utils/renderWithProviders'

import { App } from '../App'

vi.mock('hooks/useAnalytics', () => ({ useConfigureFirebase: vi.fn() }))
vi.mock('app/App/hook/useLogNavigation', () => ({ default: vi.fn() }))
vi.mock('app/App/hook/usePageTitle', () => ({ default: vi.fn() }))
vi.mock('@sentry/browser', () => ({ setUser: vi.fn() }))

const renderApp = (storeOverrides: any, url = '/') =>
  renderWithProviders(
    <>
      <div id="root"></div>

      <Routes>
        <Route path="/" element={<App />}>
          <Route path="/" element={<p>Sub component</p>} />
          <Route path="/adage-iframe" element={<p>ADAGE</p>} />
          <Route path="/offres" element={<p>Offres</p>} />
          <Route path="/connexion" element={<p>Login page</p>} />
          <Route
            path="/parcours-inscription"
            element={<p>Onboarding page</p>}
          />
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
        currentUser: {
          id: 12,
          isAdmin: false,
          hasUserOfferer: true,
        },
      },
    }
    vi.spyOn(window, 'scrollTo')
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])
  })

  it('should render App and children components when isMaintenanceActivated is false', async () => {
    renderApp(store)

    expect(await screen.findByText('Sub component')).toBeInTheDocument()
    expect(setUser).toHaveBeenCalledWith({
      id: store.user.currentUser.id.toString(),
    })
  })

  it('should render the cookie banner', async () => {
    renderApp(store)
    expect(
      await screen.findByText(
        /Nous utilisons des cookies et traceurs afin d’analyser l’utilisation de la plateforme et vous proposer la meilleure expérience possible/
      )
    ).toBeInTheDocument()
  })

  it('should redirect to login if not logged in on a private page', async () => {
    const loggedOutStore = {
      user: { currentUser: null },
    }
    renderApp(loggedOutStore, '/offres')

    expect(await screen.findByText('Login page')).toBeInTheDocument()
  })

  it('should redirect to onboarding if has no user_offerer on private page', async () => {
    const noUserOffererStore = {
      user: {
        currentUser: {
          id: 12,
          isAdmin: false,
          hasUserOfferer: false,
        },
      },
    }
    renderApp(noUserOffererStore, '/offres')

    expect(await screen.findByText('Onboarding page')).toBeInTheDocument()
  })

  it('should not initialize firebase on the adage iframe', async () => {
    vi.spyOn(cookieConsentModal, 'initCookieConsent').mockImplementation(
      () => ({
        internals: {
          manager: {
            consents: [cookieConsentModal.Consents.FIREBASE],
            watch: () => {},
          },
        },
      })
    )
    const useAnalyticsSpy = vi
      .spyOn(useAnalytics, 'useConfigureFirebase')
      .mockImplementation(() => {})

    const loggedInStore = {
      user: {
        currentUser: {
          id: 12,
        },
      },
    }
    renderApp(loggedInStore, '/adage-iframe')

    await screen.findByText('ADAGE')

    expect(useAnalyticsSpy).not.toHaveBeenCalledWith(
      expect.objectContaining({ isCookieEnabled: true })
    )
  })
})
