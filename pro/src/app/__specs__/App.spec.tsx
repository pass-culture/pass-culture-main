import { setUser } from '@sentry/browser'
import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import * as orejime from 'app/App/analytics/orejime'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { App } from '../App/App'

vi.mock('app/App/analytics/firebase', () => ({ useFirebase: vi.fn() }))
vi.mock('app/App/hook/useLogNavigation', () => ({ useLogNavigation: vi.fn() }))
vi.mock('app/App/hook/usePageTitle', () => ({ usePageTitle: vi.fn() }))
vi.mock('@sentry/browser', () => ({ setUser: vi.fn() }))

const renderApp = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(
    <>
      <div id="root" />

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
    {
      initialRouterEntries: ['/'],
      user: sharedCurrentUserFactory(),
      ...options,
    }
  )

global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value: {
    href: 'someurl',
  },
  writable: true,
})

describe('App', () => {
  beforeEach(() => {
    vi.spyOn(window, 'scrollTo')
    vi.spyOn(api, 'listFeatures').mockResolvedValue([])
  })

  it('should render App and children components when isMaintenanceActivated is false', async () => {
    const user = sharedCurrentUserFactory({ hasUserOfferer: true })
    renderApp({ user })

    expect(await screen.findByText('Sub component')).toBeInTheDocument()
    expect(setUser).toHaveBeenCalledWith({
      id: user.id.toString(),
    })
  })

  it('should render the cookie banner', async () => {
    renderApp()
    expect(
      await screen.findByText(
        /Nous utilisons des cookies et traceurs afin d’analyser l’utilisation de la plateforme et vous proposer la meilleure expérience possible/
      )
    ).toBeInTheDocument()
  })

  it('should redirect to login if not logged in on a private page', async () => {
    renderApp({ initialRouterEntries: ['/offres'], user: undefined })

    expect(await screen.findByText('Login page')).toBeInTheDocument()
  })

  it('should redirect to onboarding if has no user_offerer on private page', async () => {
    renderApp({
      user: sharedCurrentUserFactory({ hasUserOfferer: false }),
      initialRouterEntries: ['/offres'],
    })

    expect(await screen.findByText('Onboarding page')).toBeInTheDocument()
  })

  it('should not initialize firebase on the adage iframe', async () => {
    vi.spyOn(orejime, 'useOrejime').mockImplementation(() => ({
      consentedToBeamer: false,
      consentedToFirebase: false,
    }))

    const useAnalyticsSpy = vi
      .spyOn(useAnalytics, 'useFirebase')
      .mockImplementation(() => {})

    renderApp({ initialRouterEntries: ['/adage-iframe'] })

    await screen.findByText('ADAGE')

    expect(useAnalyticsSpy).not.toHaveBeenCalledWith(
      expect.objectContaining({ isCookieEnabled: true })
    )
  })
})
